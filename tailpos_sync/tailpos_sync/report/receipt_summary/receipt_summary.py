# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters, columns)

	return columns, data

def get_columns(filters):
	columns = [
		{
			"fieldname": "date",
			"label": "Transaction Date",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"fieldname": "qty",
			"label": "Quantity",
			"fieldtype": "Data",
			"width": 150
		},
	]
	return columns

def get_data(filters, columns):
	data = []

	# get values from client side
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	_items = filters.get("_items")

	print(from_date)
	print(to_date)

	data = frappe.db.sql("""
					SELECT `tabReceipts`.date, `tabReceipts Item`.item_name, `tabReceipts Item`.qty 
    				FROM `tabReceipts Item` 
    				INNER JOIN `tabReceipts` ON `tabReceipts Item`.parent = `tabReceipts`.name
    				WHERE item_name = %s
    				GROUP BY `tabReceipts`.date
    				HAVING `tabReceipts`.date >= %s AND `tabReceipts`.date <= %s """,
                         (_items, from_date, to_date), as_dict=True)


	print(data)
	return data
