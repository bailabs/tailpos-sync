import frappe
import datetime
import json
from frappe.utils.password import get_decrypted_password

#CREATE ERROR LOG
def create_error_log(message, title, data):
    error_log = frappe.log_error(message, title)
    created_error_log = frappe.get_doc("Error Log", error_log.name)
    created_error_log.device_id = data['device_id'] if "device_id" in data else ""
    created_error_log.wallet_card = data['wallet_card_number'] if "wallet_card_number" in data else ""
    created_error_log.pin = data['pin'] if "pin" in data else ""
    created_error_log.save()

#CUSTOMERS PIN CHECK
@frappe.whitelist()
def check_customers_pin(data):
    try:
        wallet_card_number = json.loads(data['scanned_nfc'])['customer']
        customers_pin = data['pin']
        wallet_data = get_wallet(wallet_card_number)
        if len(wallet_data) > 0:
            return compare_customers_pin(customers_pin, wallet_data, data)
    except:
        create_error_log(frappe.get_traceback(), 'Failed Checking Customers Pin', data)


def compare_customers_pin(customers_pin, wallet_data, data):
    password = get_decrypted_password("Wallet",wallet_data[0].name, "customer_pin")

    if customers_pin == password:
        return {"message": "Please scan attendant card" , "failed": False}
    else:
        create_error_log("Failed Checking Customers Pin", 'Customers Pin Check', data)
        return {"message": "Failed Checking Customers Pin" , "failed": True}

# GET BALANCE
@frappe.whitelist()
def get_balance(data):
    wallet_card_number = data['wallet_card_number']
    wallet_data = get_wallet(wallet_card_number)
    if len(wallet_data) > 0:
        customer_data = get_customer_credit(wallet_data[0])
        if customer_data and customer_data['credit_limit']:
            return {"data": customer_data['credit_limit'] + customer_data['total_prepaid_balance'], "failed": False}
        else:
            create_error_log("Please set up credit limit in ERPNext",'No Credit Limit',data)
            return {"message": "Please set up credit limit in ERPNext","failed": True}

    else:
        create_error_log("Customer Wallet does not exist", 'Wallet Check', data)
        return {"message": "Customer Wallet does not exist", "failed": True}

#CUSTOMER WALLET CHECK
@frappe.whitelist()
def validate_if_customer_wallet_exists(data):
    wallet_card_number = data['wallet_card_number']
    receipt = data['receipt']
    wallet_data = get_wallet(wallet_card_number)
    if len(wallet_data) > 0:
        customer_data = get_customer_credit(wallet_data[0])
        if customer_data and customer_data['credit_limit']:
            if customer_data['credit_limit'] + (customer_data['total_prepaid_balance'] - get_receipt_total(receipt)) >= 0:
                return {"message": "Please input valid customer pin", "failed": False}
            else:
                create_error_log("Insufficient Balance", "Balance Check", data)
                return {"message": "Insufficient Balance", "failed": True}
        else:
            create_error_log("Please set up credit limit in ERPNext",'No Credit Limit',data)
            return {"message": "Please set up credit limit in ERPNext","failed": True}
    else:
        create_error_log("Failed customer wallet check", 'Wallet Check', data)
        return {"message": "Failed customer wallet check", "failed": True}

#ATTENDANT WALLET CHECK
@frappe.whitelist()
def validate_if_attendant_wallet_exists(data):
    print("beeeeeeeeeeeeeee")
    wallet_card_number = data['wallet_card_number']
    attendant = frappe.db.sql(""" SELECT * FROM `tabAttendants` WHERE card_number=%s""", wallet_card_number)
    if len(attendant) > 0:
        return {"failed": False}
    create_error_log("Failed attendant wallet check", 'Attendant Wallet Check', data)
    return {"message": "Failed attendant wallet check", "failed": True}

#VALIDATE WALLET
@frappe.whitelist()
def validate_wallet(data):
    try:
        customer = json.loads(data['scanned_nfc'])['customer'] #CUSTOMER WALLET DATA FROM TAILPOS
        attendant = json.loads(data['scanned_nfc'])['attendant'] #ATTENDANT WALLET DATA FROM TAILPOS
        receipt = data['receipt'] #RECEIPT RECORD FROM TAILPOS
        device = data['device_id'] #DEVICE ID FROM TAILPOS
        receipt_total = get_receipt_total(receipt) #GET RECEIPT TOTAL
        balances = get_wallet(customer) #BALANCE BEFORE DEDUCTIONS
        update_wallet = update_wallet_card(receipt_total,balances,data) #UPDATE WALLET
        create_wallet_logs(customer,update_wallet,receipt,balances,device,attendant,data) #CREATE WALLET LOGS
        return {"message": update_wallet[0], "failed": update_wallet[1]}
    except:
        create_error_log(frappe.get_traceback(), 'Wallet Transaction Failed', data)

#UPDATE WALLET FROM RECEIPT TOTAL
def update_wallet_card(receipt_total,balances,data):

    if len(balances) > 0:
        customer_data = get_customer_credit(balances[0])
        if customer_data['credit_limit'] + (customer_data['total_prepaid_balance'] - receipt_total) >= 0:
            new_prepaid = (customer_data['total_prepaid_balance'] - receipt_total )
        else:
            create_error_log("Insufficient Balance", "Balance Check", data)
            return "Insufficient Balance", True

        frappe.db.sql(""" UPDATE `tabWallet` SET prepaid_balance=%s WHERE name=%s""",
                      (new_prepaid, balances[0].name))
        update_customer_credit(balances[0].customer)
        return "Wallet Transaction Complete", False
    else:
        create_error_log("Failed to validate wallet", "Wallet Check", data)
        return "Failed to validate wallet", True

#UPDATE CUSTOMER CREDIT
@frappe.whitelist()
def update_customer_credit(wallet_customer_name):
    total = frappe.db.sql("""SELECT SUM(prepaid_balance), company FROM tabWallet WHERE customer=%s""", wallet_customer_name)
    frappe.db.sql(""" UPDATE `tabCustomer Credit Limit` SET total_prepaid_balance=%s WHERE parent=%s """, (total[0][0],wallet_customer_name ))
    frappe.db.commit()
    return True

#GET CUSTOMER CREDIT
def get_customer_credit(wallet):
    customer = frappe.get_doc("Customer", wallet.customer)
    if customer.__dict__:
        for i in customer.credit_limits:
            if i.company == wallet.company:
                return i.__dict__
    else:
        frappe.log_error("Please Setup Customer Credit Limit", 'Wallet Transaction Failed')
#GET RECEIPT TOTAL
def get_receipt_total(receipt):
    total_amount = 0
    for i in receipt['lines']:
        total_amount = total_amount + (i['price'] * i['qty'])

    return total_amount


#CREATE WALLET LOGS
def create_wallet_logs(wallet_data,update_wallet,receipt,balances,device,attendant,data):
    if not update_wallet[1]:
        update_wallet = get_wallet(wallet_data)
        attendant_name = get_attendant(attendant)
        try:
            doc = {
                "doctype": "Wallet Logs",
                "date": datetime.datetime.strptime(receipt['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                "wallet": update_wallet[0].name,
                "prepaid_balance_before_deduction": balances[0].prepaid_balance,
                "credit_balance_before_deduction": balances[0].credit_limit,
                "amount": get_receipt_total(receipt),
                "prepaid_balance_after_deduction": update_wallet[0].prepaid_balance,
                "credit_balance_after_deduction": update_wallet[0].credit_limit,
                "attendant": attendant_name,
                "device": device,
                "top_up_wallet": 0,
            }
            frappe.get_doc(doc).insert(ignore_permissions=True)
        except:
            create_error_log(frappe.get_traceback(), 'Failed Creating Wallet Logs', data)

#GET WALLET RECORD
def get_wallet(wallet_data):
    return frappe.db.sql(""" SELECT * FROM `tabWallet` WHERE wallet_card_number=%s""", wallet_data ,as_dict=True)

#GET CUSTOMER RECORD
def get_customer(customer_name):
    return frappe.db.sql(""" SELECT * FROM `tabCustomer` WHERE name=%s""", customer_name ,as_dict=True)

#GET ATTENDANT RECORD
def get_attendant(attendant):
    return frappe.db.sql(""" SELECT user_name FROM `tabAttendants` WHERE card_number=%s """, attendant)[0][0]