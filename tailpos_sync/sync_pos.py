from sync_methods import *
import frappe
import datetime


@frappe.whitelist()
def tailpos_test(data):
    if data['type_of_query'] == "Shifts":

        shift_end_from = data['end_from'] + " 00:00:00"
        shift_end_to = data['end_to'] + " 23:59:59"
        shift_data = frappe.db.sql(""" SELECT * FROM `tabShifts` WHERE shift_end BETWEEN %s AND %s """,
                                   (shift_end_from, shift_end_to), as_dict=True)
        return {"data": shift_data}
    elif data['type_of_query'] == "Item":

        item_end_from = data['end_from']
        item_end_to = data['end_to']
        shift_data = frappe.db.sql(""" SELECT * FROM `tabReceipts` WHERE date BETWEEN %s AND %s""",
                                   (item_end_from, item_end_to), as_dict=True)
        return shift_data
    elif data['type_of_query'] == "Sales":
        sales_data = ""
        if data['type_of_filter'] == "Daily":
            sales_data = frappe.db.sql(""" SELECT * FROM `tabReceipts` WHERE MONTH(date) = %s and YEAR(date) = %s""",
                                       (data['month'], data['year']), as_dict=True)
        if data['type_of_filter'] == "Monthly":
            sales_data = frappe.db.sql(""" SELECT * FROM `tabReceipts` WHERE YEAR(date) = %s""", (data['year']),
                                       as_dict=True)
        if data['type_of_filter'] == "Yearly":
            sales_data = frappe.db.sql(""" SELECT * FROM `tabReceipts`""", as_dict=True)

        return sales_data


@frappe.whitelist()
def sync_data(data):
    trash_object = data['trashObject']
    tailpos_data = data['tailposData']
    sync_type = data['typeOfSync']
    device_id = data['deviceId']

    uom_check()
    deleted_records = deleted_documents()
    delete_records(trash_object)

    data_length = len(tailpos_data)

    for i in range(0, data_length):
        receipt_total = 0
        db_name = tailpos_data[i]['dbName']
        sync_object = tailpos_data[i]['syncObject']

        if tailpos_data[i]['dbName'] != "Company":
            if deleted_records_check(sync_object['_id'], deleted_records):
                query = "SELECT name FROM `tab{0}` WHERE id='{1}'".format(db_name, sync_object['_id'])

                try:
                    exist = frappe.db.sql(query, as_dict=True)
                except Exception:
                    print(frappe.get_traceback())

                if len(exist) > 0:
                    frappe_table = frappe.get_doc(db_name, exist[0]['name'])

                    if 'dateUpdated' in sync_object:
                        update_data = check_modified(sync_object['dateUpdated'], frappe_table)
                    else:
                        update_data = True
                    if update_data:
                        insert_data(tailpos_data[i], frappe_table, receipt_total)
                else:
                    frappe_table = new_doc(tailpos_data[i])

                    try:
                        frappe_table.insert(ignore_permissions=True)
                    except:
                        frappe.log_error(frappe.get_traceback(), 'sync failed')

    force_sync = True if sync_type == "forceSync" else False
    erpnext_data = sync_from_erpnext(device_id, force_sync)

    if not erpnext_data:
        erpnext_data = ""

    res = {
        "data": erpnext_data,
        "deleted_documents": deleted_records
    }

    return {"data": res}


def check_modified(data, frappe_table):
    date_from_pos = datetime.datetime.fromtimestamp(data / 1000.0)

    if frappe_table.modified == None:
        update_data = True
        frappe_table.db_set("date_updated", None)
    else:
        if frappe_table.modified < date_from_pos:
            update_data = True
            frappe_table.db_set('date_updated', None)
        else:
            update_data = False

    return update_data
