import frappe
import uuid


def generate_sales_invoice_daily():
    """Generate Sales Invoice from Receipts"""

    dates_query = """SELECT DATE(date) AS daily_date FROM `tabReceipts` GROUP BY DATE(date)"""

    dates = frappe.db.sql(dates_query, as_dict=1)

    for date in dates:
        generate_sales_invoice_by_date(date.daily_date)


def receipts_by_date(date):
    """Retrieve Receipts by date"""

    receipts_query = """SELECT name FROM `tabReceipts` WHERE DATE(date)=%s"""

    receipts = frappe.db.sql(receipts_query, date, as_dict=1)

    return receipts


def generate_sales_invoice_lines(name):
    """Create Sales Invoice from Receipts"""
    receipt = frappe.get_doc('Receipts', name)

    lines = []

    for line in receipt.receipt_lines:
        lines.append({
            'item_code': line.item_name,
            'item_name': line.item_name,
            'uom': 'Unit',
            'qty': line.qty,
            'rate': line.price
        })

    return lines


def generate_sales_invoice_by_date(date):
    """Create Sales Invoice"""

    receipts = receipts_by_date(date)

    sales_invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'customer': 'Guest',
        'posting_date': date,
        'due_date': date,
        'title': date,
        'update_stock': 1
    })

    for receipt in receipts:
        lines = generate_sales_invoice_lines(receipt.name)
        sales_invoice.extend('items', lines)

    shifts = shifts_by_date(date)

    settings = frappe.get_doc('TailPOS Settings', 'TailPOS Settings')

    for shift in shifts:
        shift = frappe.get_doc('Shifts', shift.name)
        short_or_over = shift.actual_money - shift.ending_cash

        item_code = settings.shortages

        if short_or_over > 0:
            item_code = settings.overages

        sales_invoice.append('items', {
            'item_code': item_code,
            'rate': short_or_over,
            'qty': 1
        })

    try:
        sales_invoice.insert()
        sales_invoice.submit()
    except Exception as e:
        print str(e)


def sync_now():
    """Generates Sales Invoice Daily"""
    from frappe.utils.background_jobs import enqueue

    settings = frappe.get_doc('TailPOS Settings', 'TailPOS Settings')

    if settings.sales_invoice == 'By Daily Batch':
        enqueue('tailpos_sync.tailpos.generate_sales_invoice_today', timeout=2000, queue='long')


def shifts_by_date(date):
    """Retrieve Shifts by date"""

    # Receipts query
    shifts_query = """SELECT name FROM `tabShifts` WHERE DATE(shift_beginning)=%s"""

    # Get all receipts
    shifts = frappe.db.sql(shifts_query, date, as_dict=1)

    return shifts


def exists_sales_invoice_by_receipt(receipt):
    """Is there an existing Sales Invoice"""
    sales_invoices = frappe.get_all('Sales Invoice', filters={'remarks': receipt})
    if sales_invoices:
        return True
    return False


@frappe.whitelist()
def save_item(doc,method):
    if doc.date_updated == None:
        doc.date_updated = doc.modified


def set_item_uuid(doc, method):
    if doc.in_tailpos and not doc.id:
        doc.id = str(uuid.uuid4())


def get_receipt_items(receipt):
    fields = ['item', 'price', 'qty']
    return frappe.get_all('Receipts Item', filters={'parent': receipt}, fields=fields)


def get_items_with_price_list_query(columns=None):
    pos_profile = frappe.db.get_single_value('Tail Settings', 'pos_profile')
    price_list = frappe.db.get_value('POS Profile', pos_profile, 'selling_price_list')

    columns_str = ', '.join(columns) if columns else '*'

    query = """SELECT %s FROM `tabItem` INNER JOIN `tabItem Price` ON `tabItem`.name = `tabItem Price`.item_code WHERE `tabItem`.in_tailpos = 1 AND `tabItem Price`.price_list='%s'""" % (columns_str, price_list)

    return query
