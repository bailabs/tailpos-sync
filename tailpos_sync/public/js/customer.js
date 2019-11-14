
cur_frm.cscript.onload = function (frm) {

    frappe.call({
        method: "tailpos_sync.wallet_sync.update_customer_credit",
        args: {
            "wallet_customer_name": cur_frm.doc.customer_name,
        },
        callback: function () {
            cur_frm.doc.refresh("credit_limits")
        }
    })

}