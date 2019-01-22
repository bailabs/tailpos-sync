
import frappe,json
import uuid


def generate_sales_invoice_daily():
    """Generate Sales Invoice from Receipts"""

    # Dates Query
    dates_query = """SELECT DATE(date) AS daily_date FROM `tabReceipts` GROUP BY DATE(date)"""

    # Get all dates from tab receipts
    dates = frappe.db.sql(dates_query, as_dict=1)

    # Hey jude
    for date in dates:
        #print 'Creating for {0}'.format(date.daily_date)
        generate_sales_invoice_by_date(date.daily_date)


def receipts_by_date(date):
    """Retrieve Receipts by date"""

    # Receipts query
    receipts_query = """SELECT name FROM `tabReceipts` WHERE DATE(date)=%s"""

    # Get all receipts
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

    # Receipts based on date
    receipts = receipts_by_date(date)

    # Create the Sales Invoice
    sales_invoice = frappe.get_doc({
        'doctype': 'Sales Invoice',
        'customer': 'Guest',
        'posting_date': date,
        'due_date': date,
        'title': date,
        'update_stock': 1
    })

    # Add receipt lines to the Sales Invoice lines
    for receipt in receipts:
        lines = generate_sales_invoice_lines(receipt.name)
        sales_invoice.extend('items', lines)

    # Add shortages or overages
    shifts = shifts_by_date(date)

    # Cash Short and Over
    settings = frappe.get_doc('TailPOS Settings', 'TailPOS Settings')

    for shift in shifts:
        shift = frappe.get_doc('Shifts', shift.name)
        short_or_over = shift.actual_money - shift.ending_cash

        #  If shortages
        item_code = settings.shortages

        # If overages
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
        #print '[/] Sales Invoice {0} has been created'.format(sales_invoice.name)
    except Exception as e:
        print str(e)


def generate_sales_invoice_from_receipt(doc, method):
    """Generates Sales Invoice based from the Receipt created"""
    # settings = frappe.get_doc('TailPOS Settings', 'TailPOS Settings')
    settings = 'By Individual'
    if settings == 'By Individual' and not exists_sales_invoice_by_receipt(doc.series):
        sales_invoice = frappe.get_doc({
            'doctype': 'Sales Invoice',
            'customer': 'Guest',
            'pos_profile': 'Sample',
            'is_pos': 1,
            'due_date': frappe.utils.nowdate(),
            'update_stock': 1,
            'remarks': 'Receipt/{0}'.format(doc.receiptnumber)
        })

        total_amount = 0

        # Get all items
        items = frappe.get_all('Receipts Item', filters={'parent': doc.id})

        for line in items:
            lines = frappe.get_doc('Receipts Item', line.name)
            sales_invoice.append('items', {
                'item_code': lines.item_name,
                'item_name': lines.item_name,
                'uom': 'Unit',
                'qty': lines.qty,
                'rate': lines.price
            })
            total_amount = total_amount + int(lines.qty) * int(lines.price)

        # One time payment
        sales_invoice.append('payments', {
            'mode_of_payment': 'Cash',
            'amount': total_amount
        })

        sales_invoice.insert(ignore_permissions=True)
        sales_invoice.submit()


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

@frappe.whitelist()
def save_customer(doc, method):

    try:
        doc.customer_group = 'All Customer Group'
    except Exception:
        print(frappe.get_traceback())
    try:
        doc.territory = 'All Territories'
    except Exception:
        print(frappe.get_traceback())

def test():
    number = frappe.db.sql("""SELECT COUNT(*) as count FROM `tabReceipts` WHERE generated=0""", as_dict=1)
    print number
