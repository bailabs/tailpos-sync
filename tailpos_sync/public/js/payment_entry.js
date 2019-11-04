

cur_frm.cscript.party = function(frm){
    if(cur_frm.doc.party){
        console.log("AJKSHDKASJHD")
        cur_frm.fields_dict['wallet_card_number'].get_query = function() {
			return {
			    filters:{
                    "customer": cur_frm.doc.party
                }
			}
		}
    }
}