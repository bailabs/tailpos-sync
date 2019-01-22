// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt
frappe.ui.form.on('Discounts', {
	refresh: function(frm) {
		frm.set_value("edit_type", 0);
		frm.set_value("from_couchdb", 0);
		frm.set_df_property("type", "read_only", frm.doc.edit_type ? 0 : 1);
	},
	edit_type: function(frm) {
		frm.set_df_property("type", "read_only", frm.doc.edit_type ? 0 : 1);
	}
});
