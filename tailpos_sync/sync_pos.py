from .sync_methods import *
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
    try:
        uom_check()
        deleted_records = get_deleted_documents()
        delete_records(trash_object)

        _sync_to_erpnext(tailpos_data, deleted_records,device_id)

        force_sync = (sync_type == "forceSync")
        erpnext_data = sync_from_erpnext(device_id, force_sync)

        if not erpnext_data:
            erpnext_data = ""

        res = {
            "data": erpnext_data,
            "deleted_documents": deleted_records
        }

        return {"data": res, "status": True}
    except:
        print(frappe.get_traceback())
        frappe.log_error(frappe.get_traceback(), 'sync failed')
        return {"status": False}

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


def _sync_to_erpnext(tailpos_data, deleted_records,device_id):
    for row in tailpos_data:
        receipt_total = 0

        db_name = row.get('dbName')
        sync_object = row.get('syncObject')

        _id = sync_object.get('_id')
        date_updated = sync_object.get('dateUpdated')

        if db_name == "Company" or is_deleted_record(_id, deleted_records):
            continue

        exist = _get_doc(db_name, _id)

        if exist:
            frappe_table = frappe.get_doc(db_name, exist[0]['name'])

            if 'dateUpdated' in sync_object:
                update_data = check_modified(date_updated, frappe_table)
            else:
                update_data = True
            if update_data:
                insert_data(row, frappe_table, receipt_total)
        else:
            frappe_table = new_doc(row)

            try:
                frappe_table.insert(ignore_permissions=True)
            except:
                frappe.log_error(frappe.get_traceback(), 'sync failed')


def _get_doc(db_name, _id):
    return frappe.db.sql("""
        SELECT name 
        FROM `tab{0}` 
        WHERE id=%(_id)s
    """.format(db_name), {'_id': _id}, as_dict=True)
