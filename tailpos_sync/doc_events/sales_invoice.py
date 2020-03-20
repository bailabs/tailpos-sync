import frappe


def validate(doc, method):
    print("=====================================================================")
    print("NAA MAN DIRI")
    print(doc.docstatus)
    if doc.docstatus == 0:
        print("diri daw")
        taxes = []
        doc.taxes = []
        total_taxes = 0
        for sales_item in doc.items:
            sales_invoice_item = sales_item.__dict__
            if sales_invoice_item['item_tax_template']:
                item_taxes = frappe.db.sql(""" SELECT * FROM `tabItem Tax Template Detail` WHERE parent=%s """,sales_invoice_item['item_tax_template'],as_dict=True)
                for i in item_taxes:
                    if i.tax_type not in taxes:
                        taxes.append(i.tax_type)
                        doc.append("taxes",{
                            "charge_type": "On Net Total",
                            "account_head": i.tax_type,
                            "rate": 0,
                            "description": i.tax_type.split("-")[0],
                            "tax_amount": (i.tax_rate / 100) * sales_invoice_item['amount'],
                            "base_tax_amount": (i.tax_rate / 100) * sales_invoice_item['amount'],
                            "total": ((i.tax_rate / 100) * sales_invoice_item['amount']) + sales_invoice_item['amount'],
                            "base_total": ((i.tax_rate / 100) * sales_invoice_item['amount']) + sales_invoice_item['amount']
                        })
                        total_taxes += (i.tax_rate / 100) * sales_invoice_item['amount']
                    else:
                        for iii in doc.taxes:
                            if iii.__dict__['account_head'] == i.tax_type:
                                iii.__dict__['tax_amount'] += (i.tax_rate / 100) * sales_invoice_item['amount']
                                iii.__dict__['base_tax_amount'] += (i.tax_rate / 100) * sales_invoice_item['amount']
                                iii.__dict__['total'] += ((i.tax_rate / 100) * sales_invoice_item['amount']) + sales_invoice_item['amount']
                                iii.__dict__['base_total'] += ((i.tax_rate / 100) * sales_invoice_item['amount']) + sales_invoice_item['amount']
                                total_taxes += (i.tax_rate / 100) * sales_invoice_item['amount']

        doc.total_taxes_and_charges = total_taxes
        doc.grand_total = total_taxes + doc.total
        doc.outstanding_amount = total_taxes + doc.total
        print("naa pud diriiiiii")
        print("=======================================================================")