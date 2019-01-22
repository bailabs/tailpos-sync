import frappe


def add_role(doc, method):
    doc.add_roles('Subscriber')
    doc.save()
