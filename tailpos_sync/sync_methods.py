import frappe, json, datetime


def insert_data(i, data, frappe_table, receipt_total):
    for key, value in data[i]['syncObject'].iteritems():
        print("nisuloddddddd")
        field_name = str(key).lower()

        if field_name == "taxes":
            value = ""
        if field_name == "soldby":
            field_name = "stock_uom"
        if field_name == "colorandshape":

            color = json.loads(value)[0]['color'].capitalize()
            if color == "Darkmagenta":
                color = "Dark Magenta"
            if color == "Darkorange":
                color = "Dark Orange"
            if color == "Firebrick":
                color = "Fire Brick"
            frappe_table.db_set("color", color)
            frappe_table.db_set("shape", json.loads(value)[0]['shape'].capitalize())
        if field_name == "colororimage":
            field_name = "color_or_image"
        if field_name == "imagepath":
            field_name = "image"
        if field_name == "price":
            field_name = "standard_rate"
        if data[i]['dbName'] != "Customer":
            if field_name == "name":
                field_name = "description"
        elif data[i]['dbName'] == "Customer":
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
            print(value)
            if value:
                if data[i]['dbName'] != "Receipts":
                    value = datetime.datetime.fromtimestamp(value / 1000.0).date()
                    print("VALUUUUEEEEEE")
                    print(value)
                else:
                    value = datetime.datetime.fromtimestamp(value / 1000.0).date()
                    print("VALUUUUEEEEEE RECEEEEEEEEEipts")
                    print(value)
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
        if data[i]['dbName'] == "Receipts":
            try:
                frappe_table.db_set("total_amount", receipt_total)
            except Exception:
                print(frappe.get_traceback())
        print("EXCEPTION")
        frappe_table.insert(ignore_permissions=True)
    except Exception:
        print(frappe.get_traceback())


def deleted_documents():
    tables = ["Item", "Categories", "Discounts", "Attendants", "Customer"]
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
    try:
        tableNames = ['Item', 'Categories', 'Discounts', 'Attendants', "Customer"]
        data = []
        for i in tableNames:
            dataFromDb = frappe.db.sql("SELECT * FROM `tab" + i + "`", as_dict=True)

            for x in dataFromDb:
                data.append({
                    'tableNames': i,
                    'syncObject': x
                })
                frappe.db.sql("UPDATE `tab" + i + "` SET `date_updated`=`modified` where id=%s", (x.id))
    except Exception:
        print(frappe.get_traceback())
    return data


def sync_from_erpnext_to_tailpos():
    table_names = ['Item', 'Categories', 'Discounts', 'Attendants', 'Customer']
    data = []
    for i in table_names:

        dataFromDb = frappe.db.sql("SELECT * FROM `tab" + i + "` WHERE `modified` > `date_updated`", as_dict=True)

        if len(dataFromDb) > 0:
            for x in dataFromDb:
                data.append({
                    'tableNames': i,
                    'syncObject': x
                })
                frappe.db.sql("UPDATE `tab" + i + "` SET `date_updated`=`modified` where id=%s", (x.id))
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


def create_doc(data, i, owner='Administrator'):
    if data[i]['dbName'] == "Item":
        try:
            frappe_table = frappe.get_doc({
                "doctype": data[i]['dbName'],
                "id": data[i]['syncObject']['_id'],
                "item_code": data[i]['syncObject']['name'],
                "item_group": "All Item Groups",
                "item_name": data[i]['syncObject']['name'],
                "owner": owner
            })

        except Exception:
            print(frappe.get_traceback())

    else:
        try:
            frappe_table = frappe.get_doc({
                "doctype": data[i]['dbName'],
                "id": data[i]['syncObject']['_id'],
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
