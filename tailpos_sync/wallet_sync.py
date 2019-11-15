import frappe
import datetime

@frappe.whitelist()
def validate_customer_wallet(data):
    print("SAMOAAAAAAAAAAAAAAAA")
    try:
        wallet_data = data['wallet'] #WALLET DATA FROM TAILPOS
        receipt = data['receipt'] #RECEIPT RECORD FROM TAILPOS
        device = data['device_id'] #DEVICE ID FROM TAILPOS
        receipt_total = get_receipt_total(receipt) #GET RECEIPT TOTAL
        balances = get_wallet(wallet_data) #BALANCE BEFORE DEDUCTIONS
        update_wallet = update_wallet_card(receipt_total,balances) #UPDATE WALLET
        create_wallet_logs(wallet_data,update_wallet,receipt,balances,device) #CREATE WALLET LOGS
    except:
        frappe.log_error(frappe.get_traceback(), 'Wallet Transaction Failed')

    return {"message": update_wallet[0], "failed": update_wallet[1] }

#UPDATE WALLET FROM RECEIPT TOTAL
def test():
    balances = get_wallet("9AF076DF")
    print(update_wallet_card(10000,balances))
def update_wallet_card(receipt_total,balances):

    if len(balances) > 0:
        customer_data = get_customer_credit(balances[0])
        if customer_data['credit_limit'] + (customer_data['total_prepaid_balance'] - receipt_total) >= 0:
            new_prepaid = (customer_data['total_prepaid_balance'] - receipt_total )
        else:
            return "Insufficient Balance", True

        frappe.db.sql(""" UPDATE `tabWallet` SET prepaid_balance=%s WHERE name=%s""",
                      (new_prepaid, balances[0].name))
        update_customer_credit(balances[0].customer)
        return "Wallet Transaction Complete", False
    else:
        return "Wallet does not exist", True
#UPDATE CUSTOMER CREDIT
@frappe.whitelist()
def update_customer_credit(wallet_customer_name):
    print(wallet_customer_name)
    total = frappe.db.sql("""SELECT SUM(prepaid_balance), company FROM tabWallet WHERE customer=%s""", wallet_customer_name)
    print(total)
    frappe.db.sql(""" UPDATE `tabCustomer Credit Limit` SET total_prepaid_balance=%s WHERE parent=%s """, (total[0][0],wallet_customer_name ))
    frappe.db.commit()
    return True

#GET CUSTOMER CREDIT
def get_customer_credit(wallet):
    customer = frappe.get_doc("Customer", wallet.customer)
    if customer.__dict__:
        for i in customer.credit_limits:
            if i.company == wallet.company:
                print(i.__dict__['credit_limit'])
                print(i.__dict__['total_prepaid_balance'])
                return i.__dict__
        else:
            frappe.log_error("Please Setup Customer Credit Limit", 'Wallet Transaction Failed')
#GET RECEIPT TOTAL
def get_receipt_total(receipt):
    total_amount = 0
    for i in receipt['lines']:
        total_amount = total_amount + (i['price'] * i['qty'])

    return total_amount

#GET WALLET RECORD
def get_wallet(wallet_data):
    return frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE wallet_card_number=%s""", wallet_data ,as_dict=True)

#CREATE WALLET LOGS
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