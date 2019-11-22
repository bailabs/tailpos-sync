import frappe


def on_submit(doc, method):
    if doc.party_type == "Customer" and doc.party and doc.top_up_wallet and doc.wallet_card_number:
        try:
            prepaid_balance = get_current_balance(doc)
            check_existing_wallet_record(doc,prepaid_balance[0].prepaid_balance)
            create_wallet_log(doc,prepaid_balance)
        except:
            print(frappe.get_traceback())

def check_existing_wallet_record(doc,prepaid_balance):
    query = frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE name=%s""", doc.wallet_card_number, as_dict=True)
    if len(query) > 0:
        frappe.db.sql(""" UPDATE `tabWallet` SET prepaid_balance=%s WHERE name=%s""", (int(doc.paid_amount) + int(prepaid_balance), doc.wallet_card_number))
        frappe.db.commit()
    else:
        frappe.throw("Wallet Does Not Exist")
def get_current_balance(doc):
    return frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE name=%s """, (doc.wallet_card_number), as_dict=True)

def create_wallet_log(doc,before_top_up_wallet_data):
    after_top_up_wallet_data = get_current_balance(doc)
    before = ["prepaid_balance_before_deduction","credit_balance_before_deduction"]
    after = ["prepaid_balance_before_top_up","credit_balance_before_top_up"]
    try:
        doc = {
            "doctype": "Wallet Logs",
            "date": doc.posting_date,
            "wallet": before_top_up_wallet_data[0].name,
            "prepaid_balance_before_top_up": before_top_up_wallet_data[0].prepaid_balance,
            "credit_balance_before_top_up": before_top_up_wallet_data[0].credit_limit,
            "amount": doc.paid_amount,
            "prepaid_balance_after_top_up": after_top_up_wallet_data[0].prepaid_balance,
            "credit_balance_after_top_up": after_top_up_wallet_data[0].credit_limit,
            "top_up_wallet": 1,
        }


        frappe.get_doc(doc).insert(ignore_permissions=True)
    except:
        print(frappe.get_traceback())

@frappe.whitelist()
def get_wallet_account():
    wallet = frappe.db.sql(""" SELECT name FROM `tabAccount` WHERE name like %s """, "%Wallet%")
    if len(wallet) > 0:
        return wallet[0]
    else:
        frappe.throw("No Wallet Account. Please Create Wallet account and set it in device")