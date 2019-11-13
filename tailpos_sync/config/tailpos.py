# import frappe
from frappe import _

def get_data():
	return [
		{
			"label": _("TailPOS"),
			"items": [
				{
					"type": "doctype",
					"name": "Attendancts",
				},
                {
                    "type": "doctype",
                    "name": "Item",
                },
                {
                    "type": "doctype",
                    "name": "Categories",
                },
                {
                    "type": "doctype",
                    "name": "Discounts",
                },
                {
                    "type": "doctype",
                    "name": "Receipts",
                },
                {
                    "type": "doctype",
                    "name": "Payments",
                },
                {
                    "type": "doctype",
                    "name": "Shifts",
                },
                {
                    "type": "doctype",
                    "name": "Device",
                },
                {
                    "type": "doctype",
                    "name": "Tail Settings",
                },
                {
                    "type": "doctype",
                    "name": "Wallet",
                },
                {
                    "type": "doctype",
                    "name": "Wallet Logs",
                }
			]
		}]