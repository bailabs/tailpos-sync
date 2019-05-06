import frappe
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
    company = frappe.db.get_value('POS Profile', pos_profile, 'company')
    receipts = frappe.get_all('Receipts', filters={'generated': 0})

    for receipt in receipts:
        si = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'is_pos': 1,
            'pos_profile': pos_profile,
            'company': company
        })

        items = get_receipt_items(receipt.name)

        for item in items:
            si.append('items', {
                'item_code': item['item'],
                'rate': item['price'],
                'qty': item['qty']
            })

        insert_invoice(si, submit_invoice)

        # ticked `Generated Sales Invoice`
        frappe.db.set_value('Receipts', receipt.name, 'generated', 1)
        frappe.db.set_value('Receipts', receipt.name, 'reference_invoice', si.name)
        frappe.db.commit()


# Helper
def insert_invoice(invoice, submit=False):
    invoice.set_missing_values()
    invoice.insert()

    invoice.payments[0].amount = invoice.outstanding_amount
    invoice.save()

    if submit and not check_items_zero_qty(invoice.items):
        invoice.submit()


def check_items_zero_qty(items):
    for item in items:
        if item.actual_qty <= 0:
            return True
