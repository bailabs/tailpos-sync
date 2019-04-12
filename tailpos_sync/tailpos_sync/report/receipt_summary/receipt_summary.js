// Copyright (c) 2016, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Receipt Summary"] = {
	"filters": [
		{
			"fieldname": ["from_date"],
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1

		},
		{
			"fieldname": ["to_date"],
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": ["_items"],
			"label": __("By Item"),
			"fieldtype": "Data",
		}
	]
}
