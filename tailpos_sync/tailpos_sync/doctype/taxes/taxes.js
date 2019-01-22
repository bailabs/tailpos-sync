// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Taxes', {
	refresh: function(frm) {
		frm.set_value("from_couchdb", 0);
	}
});
