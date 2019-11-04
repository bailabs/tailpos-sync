import frappe


def on_submit(doc, method):
    if doc.party_type == "Customer" and doc.party and doc.top_up_wallet and doc.wallet_card_number:
        check_existing_wallet_record(doc)

def check_existing_wallet_record(doc):
    if len(frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE customer=%s""", doc.party)) > 0:
        frappe.db.sql(""" UPDATE `tabWallet` SET prepaid_balance=%s WHERE customer=%s""", (doc.paid_amount, doc.party))