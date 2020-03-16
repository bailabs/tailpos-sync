# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from .other_methods import *
def get_cost_center_condition(filters,fields):
	condition = ""

	if filters.get("cost_center"):
		fields += ",`tabDevice`.name, `tabPOS Profile`.pos_profile, `tabPOS Profile`.cost_center"
		condition += "INNER JOIN `tabDevice` ON `tabReceipts`.deviceid = `tabDevice`.name " \
					 "INNER JOIN `tabPOS Profile` ON `tabPOS Profile`.name = `tabDevice`.pos_profile " \
					 "and `tabPOS Profile`.cost_center = '{0}'".format(filters.get("cost_center"))

	return condition


def get_store_condition(filters):
	condition = ""

	if filters.get("store"):
		condition += "and deviceid='{0}'".format(filters.get("store"))

	return condition

def get_fields():
	fields = '`tabReceipts`.name,' \
			 '`tabReceipts`.date,' \
			 '`tabReceipts`.receiptnumber,' \
			 '`tabReceipts`.discounttype,' \
			 '`tabReceipts`.discountvalue,' \
			 '`tabReceipts`.taxesvalue,' \
			 '`tabReceipts`.total_amount,' \
			 '`tabReceipts`.reference_invoice,' \
			 '`tabReceipts`.deviceid,' \
			 '`tabReceipts`.date_updated'
	return fields
def get_receipts(filters, data, columns):
	fields = get_fields()
	_from = str(filters.get("from_date"))
	_to = str(filters.get("to_date"))
	condition_store = get_store_condition(filters)
	condition_cost_center = get_cost_center_condition(filters,fields)
	query = """ SELECT {0} FROM `tabReceipts` {1} WHERE date BETWEEN '{2}' and '{3}' {4}""".format(fields,condition_cost_center,_from, _to,condition_store)
	receipts = frappe.db.sql(query, as_dict=True)
	for i in receipts:
		payment = frappe.db.sql(""" SELECT * FROM `tabPayments` WHERE receipt=%s""",(i.name),as_dict=True)
		sales_invoice = frappe.db.sql(""" SELECT * FROM `tabSales Invoice` WHERE name=%s""",(i.reference_invoice),as_dict=True)
		obj = {
			"transaction_date": i.date,
			"receipt_number": i.receiptnumber,
			"discount_type": i.discounttype,
			"discount_amount": i.discountvalue,
			"taxes_amount": i.taxesvalue,
			"total_amount_in_receipt": i.total_amount,
			"reference_invoice_number": i.reference_invoice or "",
			"device_id": i.deviceid or "",
			"updated_date": i.date_updated,
			"total_taxes_and_charges": sales_invoice[0].total_taxes_and_charges if len(sales_invoice) > 0 else "",
			"grand_total": sales_invoice[0].grand_total if len(sales_invoice) > 0 else "",
			"invoice_status": sales_invoice[0].status if len(sales_invoice) > 0 else "",
			"payment_date": payment[0].date,
			"paid_amount": payment[0].paid,
			"change": payment[0].change
		}
		print("PAYMEEENT")
		print(payment)
		type_object = json.loads(payment[0].type) if payment[0].type else []
		for type in type_object:
			obj[type['type']] = type['amount']
			if not any(x['fieldname'] == type['type'] for x in columns):
				columns.append({"fieldname": type['type'] , "label": type['type'], "fieldtype": "Data", "width": 150})

		data.append(obj)
def execute(filters=None):
	columns, data = [], []

	get_columns(columns)
	get_receipts(filters, data,columns)
	get_more_columns(columns)
	print(columns)
	return columns, data


