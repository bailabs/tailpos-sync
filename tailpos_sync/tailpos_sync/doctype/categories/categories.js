// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Categories', {
	refresh: function(frm) {
		frm.set_value("edit_color", 0);
		frm.set_value("from_couchdb", 0);
		frm.set_df_property("color", "read_only", frm.doc.edit_color ? 0 : 1);
	},
	edit_color: function(frm) {
		frm.set_df_property("color", "read_only", frm.doc.edit_color ? 0 : 1);
	}
});