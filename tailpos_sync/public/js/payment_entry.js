

cur_frm.cscript.party = function(frm){
    if(cur_frm.doc.party){
        cur_frm.fields_dict['wallet_card_number'].get_query = function() {
			return {
			    filters:{
                    "customer": cur_frm.doc.party
                }
			}
		}
    }
}
cur_frm.cscript.top_up_wallet = function(frm){
    if(cur_frm.doc.top_up_wallet){
        frappe.call({
            method: "tailpos_sync.doc_events.payment_entry.get_wallet_account",
            callback: function (r) {
                cur_frm.doc.paid_from = r.message
                cur_frm.refresh_field("paid_from")
            }
        })
    }
}