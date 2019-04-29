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
def pull_data(data):
    query = "SELECT name FROM `tab{0}`".format(data['doctype'])

    if data['doctype'] == "Item":
        query = "SELECT name, description, standard_rate FROM `tabItem` WHERE disabled=0"

    # Getting the resources
    res = frappe.db.sql(query, as_dict=True)

    return {"data": res}


@frappe.whitelist()
def sync_data(data):
    trash_object = data['trashObject']
    tailpos_data = data['tailposData']
    sync_type = data['typeOfSync']

    uom_check()
    deleted_records = deleted_documents()

    # Delete records
    delete_records(trash_object)

    for i in range(0, len(tailpos_data)):
        receipt_total = 0
        db_name = tailpos_data[i]['dbName']
        sync_object = tailpos_data[i]['syncObject']

        if deleted_records_check(sync_object['_id'], deleted_records):
            try:
                query = "SELECT * FROM `tab%(db)s` WHERE name='%(id)s'" % {'db': db_name, 'id': sync_object['_id']}
                exist = frappe.db.sql(query)

            except Exception:
                print(frappe.get_traceback())
            if db_name == "Receipts":
                receipt_total = add_receipt_lines(tailpos_data, i)

            if len(exist) > 0:
                frappe_table = frappe.get_doc(db_name, sync_object['_id'])
            else:
                frappe_table = create_doc(tailpos_data, i)

            update_data = check_modified(sync_object['dateUpdated'], frappe_table)

            if update_data:
                insert_data(i, tailpos_data, frappe_table, receipt_total)

    erpnext_data = ""

    if sync_type == "forceSync":
        erpnext_data = force_sync_from_erpnext_to_tailpos()
    elif sync_type == "sync":
        erpnext_data = sync_from_erpnext_to_tailpos()

    return {"data": {"data": erpnext_data, "deleted_documents": deleted_records}}


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
