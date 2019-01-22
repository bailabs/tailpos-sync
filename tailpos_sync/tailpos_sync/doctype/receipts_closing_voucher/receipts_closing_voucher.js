// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Receipts Closing Voucher', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			frm.set_value('posting_date', frappe.datetime.now_date());
		}
	},
	generate: function(frm) {
		frm.call({
			doc: frm.doc,
			method: 'generate',
			callback: function(r) {

			}
		});
	}
});
