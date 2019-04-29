import frappe

import datetime
import json

from .utils import get_items_with_price_list_query


def get_tables_for_sync():
    return ['Item', 'Customer', 'Categories', 'Discounts', 'Attendants']


def get_item_query():
    use_price_list = frappe.db.get_single_value('Tail Settings', 'use_price_list')

    columns = [
        'tabItem.id',
        'tabItem.name',
        'tabItem.stock_uom',
        'tabItem.sku',
        'tabItem.barcode',
        'tabItem.category',
        'tabItem.color',
        'tabItem.shape',
        'tabItem.color_or_image',
        'tabItem.image',
        'tabItem.favorite',
        '`tabItem Price`.price_list_rate as standard_rate'
    ]

    standard_rate = 'standard_rate'

    if use_price_list:
        standard_rate = '`tabItem Price`.price_list_rate as standard_rate'

    columns.append(standard_rate)

    return get_items_with_price_list_query(columns)


def get_table_select_query(table, force_sync=True):

    query = "SELECT * FROM `tab{0}`".format(table)

    if table == 'Item':
        query = get_item_query()

    if not force_sync:
        connector = " AND " if "WHERE" in query else " WHERE "
        query = query + connector + "`modified` > `date_updated`"

    return query


def insert_data(data, frappe_table, receipt_total):
    sync_object = data['syncObject']
    db_name = data['dbName']

    for key, value in sync_object.iteritems():
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
            frappe_table.db_set("type", "Percentage")

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
        print("EXCEPTION")
        frappe_table.insert(ignore_permissions=True)
    except Exception:
        print(frappe.get_traceback())


def deleted_documents():
    tables = get_tables_for_sync()
    tableNames = ["Items", "Categories", "Discounts", "Attendants", "Customer"]
    returnArray = []

    for i in range(0, len(tables)):

        data = frappe.db.sql(""" SELECT data FROM `tabDeleted Document` WHERE deleted_doctype=%s""", (tables[i]),
                             as_dict=True)

        for x in data:

            try:
                if json.loads(x.data)['id'] != None and x.sync_status == None:
                    returnArray.append({
                        'tableNames': tableNames[i],
                        '_id': json.loads(x.data)['id']
                    })
            except Exception:
                print(frappe.get_traceback())
            try:
                frappe.db.sql(""" UPDATE `tabDeleted Document` SET sync_status=%s WHERE data=%s""", ('true', x.data),
                              as_dict=True)
            except Exception:
                print(frappe.get_traceback())

    return returnArray


def force_sync_from_erpnext_to_tailpos():
    # Fetch all data in ERPNext for selected tables
    data = []
    tables = get_tables_for_sync()

    try:
        for table in tables:
            query = get_table_select_query(table)
            query_data = frappe.db.sql(query, as_dict=True)

            for row in query_data:
                data.append({
                    'tableNames': table,
                    'syncObject': row
                })
                frappe.db.sql("UPDATE `tab" + table + "` SET `date_updated`=`modified` where id=%s", row.id)
    except Exception:
        print(frappe.get_traceback())
    return data


def sync_from_erpnext_to_tailpos():
    # Fetch Updated or Added data in ERPNext for selected tables
    data = []
    tables = get_tables_for_sync()

    for table in tables:
        query_data = frappe.db.sql(get_table_select_query(table, False), as_dict=True)

        if len(query_data) > 0:
            for x in query_data:
                data.append({
                    'tableNames': table,
                    'syncObject': x
                })
                frappe.db.sql("UPDATE `tab" + table + "` SET `date_updated`=`modified` where id=%s", x.id)
    return data


def delete_records(data):
    for check in data:
        check_existing_deleted_item = frappe.db.sql("SELECT * FROM" + "`tab" + check['table_name'] + "` WHERE id=%s ",
                                                    (check['trashId']))
        if len(check_existing_deleted_item) > 0:
            frappe.db.sql("DELETE FROM" + "`tab" + check['table_name'] + "` WHERE id=%s ",
                          (check['trashId']))


def deleted_records_check(id, array):
    status = True
    for i in array:
        if i['_id'] == id:
            status = False
    return status


def create_doc(data, owner='Administrator'):
    print("[CREATE_DOC] ============================")
    print(data['syncObject'])
    print("[CREATE_DOC] ============================")

    if data['dbName'] == "Item":
        try:
            frappe_table = frappe.get_doc({
                "doctype": data['dbName'],
                "id": data['syncObject']['_id'],
                "item_group": "All Item Groups",
                "item_code": data['syncObject']['name'],
                "item_name": data['syncObject']['name'],
                "owner": owner
            })
        except Exception:
            print(frappe.get_traceback())
    else:
        try:
            frappe_table = frappe.get_doc({
                "doctype": data['dbName'],
                "id": data['syncObject']['_id'],
                "owner": owner
            })
        except Exception:
            print(frappe.get_traceback())

    return frappe_table


def add_receipt_lines(data, i):
    receipt_total = 0
    existLines = frappe.db.sql(
        "SELECT * FROM `tabReceipts Item` WHERE parent=%s ",
        (data[i]['syncObject']['_id']))

    if len(existLines) == 0:
        if len(data[i]['syncObject']['lines']) > 0:
            for x in range(0, len(data[i]['syncObject']['lines'])):

                receipt_total += int(data[i]['syncObject']['lines'][x]['price']) * int(
                    data[i]['syncObject']['lines'][x]['qty'])

                try:
                    doc = {'doctype': 'Receipts Item',
                           'parent': data[i]['syncObject']['_id'],
                           'parenttype': "Receipts",
                           'parentfield': "receipt_lines",
                           'item_name': data[i]['syncObject']['lines'][x]['item_name'],
                           'sold_by': data[i]['syncObject']['lines'][x]['sold_by'],
                           'price': data[i]['syncObject']['lines'][x]['price'],
                           'qty': data[i]['syncObject']['lines'][x]['qty']
                           }
                    doc1 = frappe.get_doc(doc)
                    doc1.insert(ignore_permissions=True)

                except Exception:
                    print(frappe.get_traceback())
    return receipt_total


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
    print(id)
    print("CATEGORY")
    try:
        data = frappe.db.sql(""" SELECT description FROM `tabCategories` WHERE id=%s """, (id), as_dict=True)
    except Exception:
        print(frappe.get_traceback())
    data_value = ""
    print(data)
    if len(data) > 0:
        if data[0]['description']:
            data_value = data[0]['description']
    return data_value
