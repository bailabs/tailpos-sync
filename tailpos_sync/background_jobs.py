import frappe
from frappe import _
from frappe.utils.background_jobs import enqueue
from .utils import get_receipt_items

@frappe.whitelist()
def generate_si():
    """
    Make this as a cron task.
    """
    enqueue('tailpos_sync.background_jobs.generate_si_from_receipts')


def generate_si_from_receipts():
    """
    Generates Sales Invoice based from the Receipt created.
    """
    pos_profile = frappe.db.get_single_value('Tail Settings', 'pos_profile')
    submit_invoice = frappe.db.get_single_value('Tail Settings', 'submit_invoice')
    use_device_profile = frappe.db.get_single_value('Tail Settings', 'use_device_profile')
    generate_limit = frappe.db.get_single_value('Tail Settings', 'generate_limit')
    allow_negative_stock = frappe.db.get_single_value('Stock Settings', 'allow_negative_stock')

    company = frappe.db.get_value('POS Profile', pos_profile, 'company')
    customer = frappe.db.get_value('POS Profile', pos_profile, 'customer')

    receipts = frappe.db.sql("""
        SELECT name FROM `tabReceipts`
        WHERE generated = 0
        LIMIT %(limit)s
    """, {'limit': int(generate_limit)}, as_dict=True)
    # receipts = frappe.get_all('Receipts', filters={'generated': 0})

    for receipt in receipts:
        device = frappe.db.get_value('Receipts', receipt.name, 'deviceid')
        mop = 'Cash'

        receipt_customer = None

        if not get_device(device):
            device = None

        if use_device_profile:
            if device:
                pos_profile = _get_device_pos_profile(device)
            company = frappe.db.get_value('POS Profile', pos_profile, 'company')
            receipt_customer = frappe.db.get_value('POS Profile', pos_profile, 'customer')

        customer_name = frappe.db.get_value(
            'Customer',
            receipt_customer or customer,
            'customer_name'
        )

        type = _get_receipts_payment_type(receipt.name)
        items = get_receipt_items(receipt.name)
        receipt_info = get_receipt(receipt.name)

        # if not customer:
        #     customer = get_customer(receipt_info.customer)

        debit_to = get_debit_to(company)

        if len(type) > 0:
            mop = _get_mode_of_payment(type, device=device)

        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'is_pos': 1,
            'pos_profile': pos_profile,
            'company': company,
            "debit_to": debit_to,
            "due_date": receipt_info.date,
            "customer": receipt_customer or customer,
            "customer_name": customer_name,
            "title": customer_name,
        })
        item_tax_template_record = []
        for item in items:
            item_tax_template_record += frappe.db.sql(""" SELECT item_tax_template, parent FROM `tabItem Tax` WHERE parent=%s and idx=%s""", (item['item'], 1), as_dict=True)
            si.append('items', {
                'item_code': item['item'],
                'rate': item['price'],
                'qty': item['qty'],
            })
        parent_name = _insert_invoice(si, mop, receipt_info.taxesvalue, submit_invoice, allow_negative_stock)

        for tax_template in item_tax_template_record:
            frappe.db.sql(""" 
                        UPDATE `tabSales Invoice Item` 
                        SET item_tax_template=%s 
                        WHERE item_code=%s AND parent=%s """, (tax_template.item_tax_template, tax_template.parent, parent_name))
            frappe.db.commit()
        # ticked `Generated Sales Invoice`
        frappe.db.set_value('Receipts', receipt.name, 'generated', 1)
        frappe.db.set_value('Receipts', receipt.name, 'reference_invoice', si.name)
        frappe.db.commit()


# Helper
def get_debit_to(company):
    return frappe.db.get_value("Company", company, "default_receivable_account")
    # return frappe.db.sql(""" SELECT name FROM `tabAccount` WHERE name like %s """, "%Debtors%")[0][0]


def _insert_invoice(invoice, mop, taxes_total, submit=False, allow_negative_stock=False):
    invoice.insert()
    if len(mop) > 0:
        for x in mop:
            invoice.append('payments', {
                'mode_of_payment': x['mode_of_payment'],
                'amount': x['amount']
            })
    else:
        invoice.append('payments', {
            'mode_of_payment': "Cash",
            'amount': invoice.outstanding_amount
        })
    invoice.set_missing_values()
    invoice.save()
    frappe.db.set_value("Sales Invoice", invoice.name, "tax_category", "")

    check_stock_qty = _check_items_zero_qty(invoice.items)
    if check_stock_qty and allow_negative_stock:
        check_stock_qty = False

    if submit and not check_stock_qty:
        invoice.submit()
        from frappe.utils import money_in_words
        frappe.db.set_value("Sales Invoice", invoice.name, "total_taxes_and_charges", taxes_total)
        frappe.db.set_value("Sales Invoice", invoice.name, "total_taxes_and_charges", taxes_total)
        frappe.db.set_value("Sales Invoice", invoice.name, "grand_total", float(invoice.grand_total) + float(taxes_total))
        frappe.db.set_value("Sales Invoice", invoice.name, "rounded_total", round(float(invoice.grand_total) + float(taxes_total)))
        frappe.db.set_value("Sales Invoice", invoice.name, "outstanding_amount", round(float(invoice.grand_total) + float(taxes_total)))
        frappe.db.set_value("Sales Invoice", invoice.name, "paid_amount", round(float(invoice.grand_total) + float(taxes_total)))
        frappe.db.set_value("Sales Invoice", invoice.name, "in_words", money_in_words(round(float(invoice.grand_total) + float(taxes_total)), invoice.currency))
        frappe.db.commit()
    return invoice.name
def get_device(device):
    device_data = frappe.db.sql(""" SELECT * FROM `tabDevice` WHERE name=%s """, device)
    if len(device_data) > 0:
        return True
    return False
def _check_items_zero_qty(items):
    for item in items:
        if item.actual_qty <= 0:
            return True

def _get_device_pos_profile(device):
    return frappe.db.get_value('Device', device, 'pos_profile')


def _get_receipts_payment_type(receipt):
    payment = frappe.db.sql_list("""SELECT name FROM `tabPayments` WHERE receipt=%s""", receipt)
    return frappe.db.sql(""" SELECT * FROM `tabPayment Types` WHERE parent=%s """, payment[0], as_dict=True)

def _get_mode_of_payment(type, device=None):
    if device:
        return _get_device_mode_of_payment(device, type)
    mode_of_payment = []
    for i in type:
        mop = frappe.get_all('Tail Settings Payment', filters={'payment_type': i.type}, fields=['mode_of_payment'])

        if not mop:
            frappe.throw(
                _('Set the mode of payment for {} in Tail Settings'.format(i.type))
            )
        else:
            mode_of_payment.append({
                "mode_of_payment": mop[0].mode_of_payment,
                "amount": i.amount
            })
    return mode_of_payment


def _get_device_mode_of_payment(device, type):
    mode_of_payment = []
    for i in type:
        mop = frappe.get_all('Device Payment', filters={'parent': device, 'payment_type': i.type}, fields=['mode_of_payment'])

        if not mop:
            frappe.throw(
                _('Set the device mode of payment for {} in device {}'.format(i.type,device))
            )
        else:
            mode_of_payment.append({
                "mode_of_payment": mop[0].mode_of_payment,
                "amount": i.amount
            })
    return mode_of_payment


def get_receipt(receipt_name):
    return frappe.db.sql(""" SELECT * FROM tabReceipts WHERE name=%s""",receipt_name, as_dict=True)[0]


def get_customer(id):
    return frappe.db.sql(""" SELECT * FROM tabCustomer WHERE id=%s""",id, as_dict=True)[0].name


def test(receipt,device):
    pos_profile = _get_device_pos_profile(device)
    submit_invoice = frappe.db.get_single_value('Tail Settings', 'submit_invoice')

    allow_negative_stock = frappe.db.get_single_value('Stock Settings', 'allow_negative_stock')

    customer = frappe.db.get_value('POS Profile', pos_profile, 'customer')

    company = frappe.db.get_value('POS Profile', pos_profile, 'company')
    type = _get_receipts_payment_type(receipt)
    items = get_receipt_items(receipt)
    receipt_info = get_receipt(receipt)
    if type:
        mop = _get_mode_of_payment(type, device=device)

    si = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'is_pos': 1,
        'pos_profile': pos_profile,
        'company': company,
        "debit_to": get_debit_to(company),
        "due_date": receipt_info.date,
        "customer": customer
    })

    for item in items:
        si.append('items', {
            'item_code': item['item'],
            'rate': item['price'],
            'qty': item['qty']
        })

    _insert_invoice(si, mop, receipt_info.taxesvalue, submit_invoice, allow_negative_stock)