// Copyright (c) 2016, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["POS Sales Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1

		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "store",
			"label": __("Store"),
			"fieldtype": "Link",
			"options": "Device"

		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center"

		}
	]
};
