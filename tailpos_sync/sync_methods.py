import frappe

import datetime
import json

from .utils import get_items_with_price_list_query,get_device_categories


def get_tables_for_sync():
    return ['Item', 'Customer', 'Categories', 'Discounts', 'Attendants']


def get_item_query(pos_profile,device):
    use_price_list = frappe.db.get_single_value('Tail Settings', 'use_price_list')

    columns = [
        'tabItem.id',
        'tabItem.sku',
        'tabItem.name',
        'tabItem.color',
        'tabItem.shape',
        'tabItem.image',
        'tabItem.barcode',
        'tabItem.category',
        'tabItem.favorite',
        'tabItem.stock_uom',
        'tabItem.item_name',
        'tabItem.color_or_image',
        '`tabItem Tax`.item_tax_template'
    ]

    standard_rate = 'standard_rate'

    if use_price_list:
        standard_rate = '`tabItem Price`.price_list_rate as standard_rate'

    columns.append(standard_rate)

    return get_items_with_price_list_query(device,columns, pos_profile)
def get_category_query(device):
    categories = get_device_categories(device)
    condition = ""
    if len(categories) > 0:
        condition += "WHERE ("

        for idx,category in enumerate(categories):
            condition += "name='{0}'".format(category)
            if int(idx) < int(len(categories) - 1):
                condition += " OR "

        condition += ")"

    query = """SELECT * FROM `tabCategories` {0}""".format(condition)
    return query
def test():
    pos_profile = frappe.db.get_value('Device', "f2ef25d668", 'pos_profile')
    get_table_select_query("Item", "f2ef25d668", True, pos_profile)

def get_table_select_query(table,device, force_sync=True, pos_profile=None):
    query = "SELECT * FROM `tab{0}`".format(table)
    if table == 'Item':
        query = get_item_query(pos_profile,device)
    if table == "Categories":
        query = get_category_query(device)
    if not force_sync:
        connector = " AND " if "WHERE" in query else " WHERE "
        if table == "Item":
            query = query + connector + "`tabItem`.modified > `tabItem`.date_updated" \
                                        ""
        else:
            query = query + connector + "`modified` > `date_updated`"

    return query


def insert_data(data, frappe_table, receipt_total):
    sync_object = data['syncObject']
    db_name = data['dbName']
    for key, value in sync_object.items():
        field_name = str(key).lower()

        if field_name == "taxes":
            value = ""

        if field_name == "soldby":
            field_name = "stock_uom"

        if field_name == "colorandshape":
            color = json.loads(value)[0]['color'].capitalize()
            color_fix = {
                'Darkmagenta': 'Dark Magenta',
                'Darkorange': 'Dark Orange',
                'Firebrick': 'Fire Brick'
            }
            if color in color_fix.keys():
                color = color_fix[color]
            frappe_table.db_set("color", color)
            frappe_table.db_set("shape", json.loads(value)[0]['shape'].capitalize())

        if field_name == "colororimage":
            field_name = "color_or_image"

        if field_name == "imagepath":
            field_name = "image"

        if field_name == "price":
            field_name = "standard_rate"

        if db_name != "Customer":
            if field_name == "name":
                field_name = "description"

        elif db_name == "Customer":
            if field_name == "name":
                field_name = "customer_name"

        if field_name == "category":
            category_value = get_category(value)
            value = category_value

        if value == "No Category":
            value = ""

        if value == "fixDiscount":
            frappe_table.db_set("type", "Fix Discount")

        if value == "percentage":
            frappe_table.db_set("discountType", "Percentage")

        if field_name == "date":
            if value:
                if db_name != "Receipts":
                    value = datetime.datetime.fromtimestamp(value / 1000.0).date()
                else:
                    value = datetime.datetime.fromtimestamp(value / 1000.0).date()
        elif field_name == "shift_beginning" or field_name == "shift_end":
            if value:
                value = datetime.datetime.fromtimestamp(value / 1000.0)
        elif field_name == "lines":
            value = json.dumps(value)
        try:
            frappe_table.db_set(field_name, value)
        except:
            None
    try:
        if db_name == "Receipts":
            try:
                frappe_table.db_set("total_amount", receipt_total)
            except Exception:
                print(frappe.get_traceback())
    except Exception:
        print(frappe.get_traceback())


def get_deleted_documents():
    tables = get_tables_for_sync()
    res = []

    for table in tables:
        deleted_docs = frappe.get_all(
            'Deleted Document',
            fields=['name', 'data', 'sync_status'],
            filters={'deleted_doctype': table}
        )

        for deleted_doc in deleted_docs:
            name = deleted_doc.get('name')
            sync_status = deleted_doc.get('sync_status', None)

            data = json.loads(deleted_doc.data)
            data_id = data.get('id', None)

            if data_id and sync_status is None:
                res.append({'tableNames': table, '_id': data_id})

                frappe.db.sql("""
                    UPDATE `tabDeleted Document`
                    SET sync_status=%s
                    WHERE name=%s
                """, ('true', name))

    frappe.db.commit()
    return res


def sync_from_erpnext(device=None, force_sync=True):
    data = []
    tables = get_tables_for_sync()
    pos_profile = frappe.db.get_value('Device', device, 'pos_profile')

    default_company = get_default_company(device)
    data.extend(default_company)

    for table in tables:
        query = get_table_select_query(table,device, force_sync, pos_profile=pos_profile)
        query_data = frappe.db.sql(query, as_dict=True)
        if table == "Item":
            for i in query_data:
                if 'item_tax_template' in i:
                    item_tax_details = frappe.db.sql(""" SELECT tax_type, tax_rate FROM `tabItem Tax Template Detail` WHERE parent=%s""", i.item_tax_template ,as_dict=True)
                    item_tax_details_split = []
                    for iii in item_tax_details:
                        item_tax_details_split.append({
                            "tax_type": iii.tax_type.split("-")[0],
                            "tax_rate": iii.tax_rate
                        })
                    i.item_tax_template_detail = item_tax_details_split

        sync_data = update_sync_data(query_data, table)

        if sync_data:
            data.extend(sync_data)

    return data


def delete_records(data):
    for check in data:
        table_name = check.get('table_name')
        trash_id = check.get('trashId')

        records = frappe.get_all(table_name, filters={'id': trash_id}, fields=['name'])

        if records:
            frappe.db.sql("DELETE FROM" + "`tab" + table_name + "` WHERE id=%s", trash_id)


def is_deleted_record(_id, deleted_records):
    for deleted_record in deleted_records:
        if deleted_record['_id'] == _id:
            return True
    return False


def new_doc(data, owner='Administrator'):
    db_name = data['dbName']
    sync_object = data['syncObject']

    doc = {
        'doctype': db_name,
        'owner': owner,
        'id': sync_object['_id'],
    }

    if db_name == 'Item':
        doc.update({
            'item_group': 'All Item Groups',
            'item_name': sync_object['name'],
            'item_code': sync_object['name'],
            'sku': sync_object['sku'],
            'barcode': sync_object['barcode'],
            'standard_rate': sync_object['price']
        })

    elif db_name == 'Customer':
        doc.update({
            'customer_name': sync_object['name']
        })

    elif db_name == 'Categories':
        doc.update({
            'description': sync_object['name']
        })

    elif db_name == 'Discounts':
        percentage_type = sync_object.get('percentageType')
        doc.update({
            'description': sync_object['name'],
            'value': sync_object['value'],
            'percentagetype': percentage_type,
            'type': _get_discount_type(percentage_type)
        })

    elif db_name == 'Attendants':
        doc.update({
            'user_name': sync_object['user_name'],
            'pin_code': sync_object['pin_code'],
            'role': sync_object['role']
        })

    elif db_name == 'Shifts':
        doc.update({
            'attendant': sync_object['attendant'],
            'beginning_cash': sync_object['beginning_cash'],
            'ending_cash': sync_object['ending_cash'],
            'actual_money': sync_object['actual_money'],
            'shift_end': get_date_fromtimestamp(sync_object['shift_end']),
            'shift_beginning': get_date_fromtimestamp(sync_object['shift_beginning'])
        })

    elif db_name == 'Payments':
        doc.update({
            'paid': sync_object['paid'],
            'receipt': sync_object['receipt'],
            'date': get_date_fromtimestamp(sync_object['date']),
            'payment_types': get_payment_types(sync_object['type'])
        })
    elif db_name == 'Receipts':
        doc.update({
            'status': sync_object['status'].capitalize(),
            'shift': sync_object['shift'],
            'roundoff': sync_object['roundOff'],
            'customer': sync_object['customer'],
            'attendant': sync_object['attendant'],
            'taxesvalue': round(sync_object['taxesAmount'],2),
            'discount': sync_object['discount'],
            'reason': sync_object['reason'],
            'deviceid': sync_object['deviceId'],
            'discountvalue': sync_object['discountValue'],
            'receiptnumber': sync_object['receiptNumber'],
            'discounttype': sync_object['discountType'].title(),
            'date': get_date_fromtimestamp(sync_object['date']),
            'receipt_lines': get_receipt_lines(sync_object['lines']),
            'receipt_taxes': get_taxes(sync_object['lines']),
            'subtotal': subtotal(sync_object['lines']),
        })

    return frappe.get_doc(doc)

def get_payment_types(payment):
    _payment_types = []

    payment_types = json.loads(payment)
    for type in payment_types:
        _payment_types.append({
            "type": type['type'],
            "amount": type['amount'],
        })
    return _payment_types

def get_taxes(lines):
    receipt_taxes = []

    for line in lines:
        tax_in_line = json.loads(line['tax'])
        for i in tax_in_line:
            if len(receipt_taxes) > 0:
                if not any(x['tax'] == i['tax_type'] for x in receipt_taxes):
                    receipt_taxes.append({
                        'tax': i['tax_type'],
                        'amount': (i['tax_rate'] / 100) * (line['qty'] * line['price']),
                    })
                else:
                    for ii in receipt_taxes:
                        if ii['tax'] == i['tax_type']:
                            ii['amount'] += (i['tax_rate'] / 100) * (line['qty'] * line['price'])
            else:
                receipt_taxes.append({
                    'tax': i['tax_type'],
                    'amount': (i['tax_rate'] / 100) * (line['qty'] * line['price']),
                })
    return receipt_taxes
def get_receipt_lines(lines):
    receipt_lines = []

    for line in lines:
        taxes_in_string = ""
        tax_in_line = json.loads(line['tax'])
        tax_total = 0

        for i in tax_in_line:
            tax_total += (i['tax_rate'] / 100) * (line['qty'] * line['price'])
            taxes_in_string += i['tax_type'] + "  -  " + str(i['tax_rate'])
        receipt_lines.append({
            'item': line['item'],
            'item_name': line['item_name'],
            'sold_by': line['sold_by'],
            'price': line['price'],
            'qty': line['qty'],
            'item_total_tax': tax_total,
            'taxes': taxes_in_string
        })

    return receipt_lines


def subtotal(lines):
    subtotal = 0

    for line in lines:
        subtotal = subtotal + (line['price'] * line['qty'])

    return subtotal

def uom_check():
    each = frappe.db.sql(""" SELECT * FROM `tabUOM` WHERE name='Each'""")

    if len(each) == 0:
        try:
            frappe.get_doc({
                'doctype': 'UOM',
                'name': 'Each',
                'uom_name': 'Each'
            }).insert(ignore_permissions=True)
        except Exception:
            print(frappe.get_traceback())

    weight = frappe.db.sql(""" SELECT * FROM `tabUOM` WHERE name='Weight'""")
    if len(weight) == 0:
        frappe.get_doc({
            'doctype': 'UOM',
            'name': 'Weight',
            'uom_name': 'Weight'
        }).insert(ignore_permissions=True)


def get_category(id):
    try:
        data = frappe.db.sql(""" SELECT description FROM `tabCategories` WHERE id=%s """, (id), as_dict=True)
    except Exception:
        print(frappe.get_traceback())
    data_value = ""
    if len(data) > 0:
        if data[0]['description']:
            data_value = data[0]['description']
    return data_value


def get_date_fromtimestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000.0).date()


def update_sync_data(data, table):
    res = []

    for datum in data:
        res.append({
            'tableNames': table,
            'syncObject': datum
        })
        frappe.db.sql("UPDATE `tab" + table + "` SET `date_updated`=`modified` where id=%s", datum.id)

    return res


def get_default_company(device):
    default_company = frappe.get_single('Tail Settings')
    default_company_from_device = frappe.db.get_value('Device', device, 'company')
    if default_company_from_device:
        default_company.company_name = default_company_from_device
    res = []
    res.append({
        'tableNames': "Company",
        'syncObject': default_company
    })
    return res

def _get_discount_type(percentage_type):
    discount_type = {
        'fixDiscount': 'Fix Discount',
        'percentage': 'Percentage'
    }
    return discount_type[percentage_type]
