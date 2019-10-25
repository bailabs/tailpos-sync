import frappe
from frappe import _
from frappe.utils.background_jobs import enqueue
from .utils import get_receipt_items


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
    print("GENERAAAATE LIMIIIIT")
    print(generate_limit)
    company = frappe.db.get_value('POS Profile', pos_profile, 'company')

    receipts = frappe.db.sql("""
        SELECT name FROM `tabReceipts`
        WHERE generated = 0
        LIMIT %(limit)s
    """, {'limit': int(generate_limit)}, as_dict=True)
    # receipts = frappe.get_all('Receipts', filters={'generated': 0})

    for receipt in receipts:
        device = None
        mop = 'Cash'

        if use_device_profile:
            device = frappe.db.get_value('Receipts', receipt.name, 'deviceid')
            pos_profile = _get_device_pos_profile(device)
            company = frappe.db.get_value('POS Profile', pos_profile, 'company')

        type = _get_receipts_payment_type(receipt.name)
        items = get_receipt_items(receipt.name)
        receipt_info = get_receipt(receipt.name)
        customer = get_customer(receipt_info.customer)
        if type:
            mop = _get_mode_of_payment(type[0], device=device)
        print("CUSTOMER")
        print(customer)
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'is_pos': 1,
            'pos_profile': pos_profile,
            'company': company,
            "debit_to": "Debtors - BWAML",
            "due_date": receipt_info.date,
            "customer": customer.customer_name
        })
        print(receipt.name)
        for item in items:
            si.append('items', {
                'item_code': item['item'],
                'rate': item['price'],
                'qty': item['qty']
            })

        _insert_invoice(si, mop, receipt_info.taxesvalue, submit_invoice,allow_negative_stock)

        # ticked `Generated Sales Invoice`
        frappe.db.set_value('Receipts', receipt.name, 'generated', 1)
        frappe.db.set_value('Receipts', receipt.name, 'reference_invoice', si.name)
        frappe.db.commit()


# Helper
def _insert_invoice(invoice, mop,taxes_total, submit=False,allow_negative_stock=False):
    invoice.set_missing_values()
    invoice.insert()
    print(mop)
    invoice.append('payments', {
        'mode_of_payment': mop.mode_of_payment,
        'amount': invoice.outstanding_amount
    })
    invoice.save()

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


def _check_items_zero_qty(items):
    for item in items:
        if item.actual_qty <= 0:
            return True

def _get_device_pos_profile(device):
    return frappe.db.get_value('Device', device, 'pos_profile')


def _get_receipts_payment_type(receipt):
    return frappe.db.sql_list("""SELECT type FROM `tabPayments` WHERE receipt=%s""", receipt)


def _get_mode_of_payment(type, device=None):
    if device:
        return _get_device_mode_of_payment(device, type)

    # DEPRECATED
    # if type == 'Cash':
    #     mode_of_payment = frappe.db.get_single_value('Tail Settings', 'cash_mop')
    # elif type == 'Card':
    #     mode_of_payment = frappe.db.get_single_value('Tail Settings', 'card_mop')

    mop = frappe.get_all('Tail Settings Payment', filters={'payment_type': type}, fields=['mode_of_payment'])

    if not mop:
        frappe.throw(
            _('Set the mode of payment for {}'.format(type))
        )

    return mop[0]


def _get_device_mode_of_payment(device, type):
    # DEPRECATED
    # if type == 'Cash':
    #     return frappe.db.get_value('Device', device, 'cash_mop')
    # elif type == 'Card':
    #     return frappe.db.get_value('Device', device, 'card_mop')
    print(device)
    print(type)
    mop = frappe.get_all('Device Payment', filters={'parent': device, 'payment_type': type}, fields=['mode_of_payment'])
    print(mop)
    if not mop:
        frappe.throw(
            _('Set the device mode of payment for {}'.format(type))
        )

    return mop

def get_receipt(receipt_name):
    return frappe.db.sql(""" SELECT * FROM tabReceipts WHERE name=%s""",receipt_name, as_dict=True)[0]

def get_customer(id):
    return frappe.db.sql(""" SELECT * FROM tabCustomer WHERE id=%s""",id, as_dict=True)[0]

def test():
    _get_mode_of_payment('Visa')
    _get_device_mode_of_payment('5663d5f38d', 'Visa')
