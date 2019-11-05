import frappe
import datetime

@frappe.whitelist()
def validate_customer_wallet(data):
    print("CHECK")
    print(data)
    try:
        wallet_data = data['wallet'] #WALLET DATA FROM TAILPOS
        receipt = data['receipt'] #RECEIPT RECORD FROM TAILPOS
        device = data['device_id'] #DEVICE ID FROM TAILPOS
        receipt_total = get_receipt_total(receipt) #GET RECEIPT TOTAL
        balances = get_wallet(wallet_data) #BALANCE BEFORE DEDUCTIONS
        update_wallet = update_wallet_card(wallet_data,receipt_total) #UPDATE WALLET
        create_wallet_logs(wallet_data,update_wallet,receipt,balances,device) #CREATE WALLET LOGS

        return {"message": update_wallet[0], "failed": update_wallet[1] }
    except:
        print(frappe.get_traceback())
def update_wallet_card(wallet_data,receipt_total):
    wallet_record = get_wallet(wallet_data)
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

def get_wallet(wallet_data):
    return frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE wallet_card_number=%s""", wallet_data ,as_dict=True)

def create_wallet_logs(wallet_data,update_wallet,receipt,balances,device):
    if not update_wallet[1]:
        update_wallet = get_wallet(wallet_data)
        print("ADDING WALLET LOGS....")
        print(receipt['date'])
        try:
            doc = {
                "doctype": "Wallet Logs",
                "date": datetime.datetime.strptime(receipt['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                "wallet": update_wallet[0].name,
                "prepaid_balance_before_deduction": balances[0].prepaid_balance,
                "credit_balance_before_deduction": balances[0].credit_limit,
                "amount": get_receipt_total(receipt),
                "prepaid_after_before_deduction": update_wallet[0].prepaid_balance,
                "credit_balance_after_deduction": update_wallet[0].credit_limit,
                "attendant": receipt['attendant'],
                "device": device,
            }
            frappe.get_doc(doc).insert(ignore_permissions=True)
        except:
            print(frappe.get_traceback())