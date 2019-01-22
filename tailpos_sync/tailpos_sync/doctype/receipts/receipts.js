// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Receipts', {
	refresh: function(frm) {
		frm.set_read_only();
		// frm.disable_save();
		// if (frm.doc.discount == "") {
		// 	frm.set_value("discount", "No Discount");
		// 	frm.set_df_property("discounttype", "hidden", 1);
		// 	frm.set_df_property("discountvalue", "hidden", 1);
		// }
	}
});
