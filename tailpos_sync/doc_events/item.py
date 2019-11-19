from tailpos_sync.utils import set_date_updated, set_doc_id
import frappe
import uuid

def validate(doc, method):
    set_date_updated(doc)


def before_save(doc, method):
    if doc.in_tailpos:
        set_doc_id(doc)

@frappe.whitelist()
def save_no_id():
    item_that_has_no_id = frappe.get_list('Item', filters={"id": ""}, fields=['*'])
    if len(item_that_has_no_id) > 0:
        for i in item_that_has_no_id:
            if not i.id:
                item_data = frappe.get_doc('Item', i.name)
                frappe.db.sql(""" UPDATE tabItem SET id=%s WHERE name=%s """,(str(uuid.uuid4()), i.name))
                frappe.db.commit()
        frappe.throw("Done Updating")
    else:
        frappe.throw("No Item Will be Updated")
