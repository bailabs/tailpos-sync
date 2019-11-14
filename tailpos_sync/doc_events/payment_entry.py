import frappe


def on_submit(doc, method):
    if doc.party_type == "Customer" and doc.party and doc.top_up_wallet and doc.wallet_card_number:
        try:
            prepaid_balance = get_current_balance(doc)
            check_existing_wallet_record(doc,prepaid_balance[0].prepaid_balance)
        except:
            print(frappe.get_traceback())
def check_existing_wallet_record(doc,prepaid_balance):
    if len(frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE name=%s""", doc.wallet_card_number)) > 0:
        print("UPDAAAAAAAAAAAATE")
        frappe.db.sql(""" UPDATE `tabWallet` SET prepaid_balance=%s WHERE name=%s""", (int(doc.paid_amount) + int(prepaid_balance), doc.wallet_card_number))
        frappe.db.commit()
    else:
        frappe.throw("Wallet Does Not Exist")
def get_current_balance(doc):
    return frappe.db.sql(""" SELECT prepaid_balance FROM `tabWallet` WHERE name=%s """, (doc.wallet_card_number), as_dict=True)

@frappe.whitelist()
def get_wallet_account():
    wallet = frappe.db.sql(""" SELECT name FROM `tabAccount` WHERE name like %s """, "%Wallet%")[0]
    if len(wallet) > 0:
        return wallet[0]
    else:
        frappe.throw("No Wallet Account. Please Create Wallet account and set it in device")