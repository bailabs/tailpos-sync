import frappe


def validate(doc, method):
    if doc.docstatus == 0 and doc.receipt:
        doc.net_total = 0
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
                            "charge_type": "Actual",
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

def before_submit(doc, method):
    if doc.receipt:
        doc.change_amount = 0
        doc.base_change_amount = 0
        doc.outstanding_amount = 0
        doc.posting_date = doc.due_date

def after_submit(doc, method):
    if doc.receipt:
        doc.posting_date = doc.due_date