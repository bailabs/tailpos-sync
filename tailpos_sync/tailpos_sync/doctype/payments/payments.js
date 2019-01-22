// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payments', {
	init_form: function(frm) {
		frm.disable_save();
		frm.add_custom_button('View Receipt', function () {
			frappe.set_route('Form', 'Receipts', frm.doc.receipt);
		});
		frm.custom_buttons['View Receipt'].addClass('btn-primary');
	},
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.trigger('init_form');
        }
	}
});
