// Copyright (c) 2018, Bai Web and Mobile Lab and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tail Settings', {
	refresh: function(frm) {

	}
});
cur_frm.cscript.update_items_with_no_tailpos_id = function () {

	frappe.call({
		method: "tailpos_sync.doc_events.item.save_no_id",
	})

}