import frappe

@frappe.whitelist()
def validate_customer_wallet(data):
    print("naa naaaa")
    print(data)
    wallet_data = data['wallet']
    receipt = data['receipt']
    receipt_total = get_receipt_total(receipt)
    print(receipt_total)
    update_wallet = update_wallet_card(wallet_data,receipt_total)

    return {"message": update_wallet[0], "failed": update_wallet[1] }

def update_wallet_card(wallet_data,receipt_total):
    wallet_record = frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE wallet_card_number=%s""", wallet_data ,as_dict=True)

    if len(wallet_record) > 0:
        new_prepaid = wallet_record[0].prepaid_balance
        new_credit = wallet_record[0].credit_limit
        if new_prepaid >= receipt_total:
            new_prepaid = new_prepaid - receipt_total
        elif new_credit >= receipt_total:
            new_credit = new_credit - receipt_total
        else:
            return "Insufficient Balance", True
        frappe.db.sql(""" UPDATE `tabWallet` SET prepaid_balance=%s, credit_limit=%s WHERE name=%s""",
                      (new_prepaid, new_credit, wallet_record[0].name))
        return "Wallet Transaction Complete", False
    else:
        return "Wallet does not exist", True

def get_receipt_total(receipt):
    total_amount = 0
    for i in receipt['lines']:
        total_amount = total_amount + (i['price'] * i['qty'])

    return total_amount