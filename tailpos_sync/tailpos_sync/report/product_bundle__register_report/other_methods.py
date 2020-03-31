import frappe



def get_columns(columns):
    columns.append({"fieldname": "invoice_date", "label": "Invoice Date", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "invoice_number", "label": "Invoice Number", "fieldtype": "Data", "width": 150, })
    columns.append({"fieldname": "receipt_no", "label": "Receipt Number", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "receipt_date", "label": "Receipt Date", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "cost_center", "label": "Cost Center", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "pos_profile", "label": "POS Profile", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "store_id", "label": "Store ID", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "uom", "label": "UOM", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "qty", "label": "QTY", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "rate", "label": "Rate", "fieldtype": "Float", "width": 150, "precision" : 2})
    columns.append({"fieldname": "amount", "label": "Amount", "fieldtype": "Float", "width": 150, "precision" : 2})
    columns.append({"fieldname": "", "label": "Packed Items", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_item_code", "label": "Item Code", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_item_name", "label": "Item Name", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_qty", "label": "Qty", "fieldtype": "Float", "width": 150, "precision" : 2})
    columns.append({"fieldname": "packed_uom", "label": "UOM", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_valuation_rate", "label":"Valuation Rate", "fieldtype": "Float", "width": 150, "precision" : 2})

def get_invoices(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    print(from_date)
    print(to_date)
    fields = [
        "SI.posting_date as invoice_date",
        "SI.name as invoice_number",
        "R.receiptnumber as receipt_no",
        "R.date as receipt_date",
        "R.deviceid as store_id",
        "D.pos_profile as pos_profile",
        "PP.cost_center as cost_center",
        "SII.item_code as item_code",
        "SII.item_name as item_name",
        "SII.uom as uom",
        "SII.qty as qty",
        "SII.rate as rate",
        "SII.amount as amount",
        "PI.item_code as packed_item_code",
        "PI.item_name as packed_item_name",
        "PI.qty as packed_qty",
        "PI.uom as packed_uom",
        "I.valuation_rate as packed_valuation_rate"
    ]

    query = """ 
        SELECT {0} FROM `tabSales Invoice` AS SI
        INNER JOIN `tabReceipts` AS R ON SI.name = R.reference_invoice
        INNER JOIN `tabSales Invoice Item` AS SII ON SII.parent = SI.name
        INNER JOIN `tabItem` AS I ON I.name = SII.item_code
        INNER JOIN `tabPacked Item` AS PI ON PI.parent = SI.name and PI.parent_item = SII.item_code
        INNER JOIN `tabDevice` AS D ON  D.name = R.deviceid
        INNER JOIN `tabPOS Profile` AS PP ON PP.name = D.pos_profile
        WHERE SI.posting_date BETWEEN '{1}' AND '{2}' ORDER BY SI.name,SII.item_code
    """.format((',').join(fields),from_date,to_date)
    print(query)
    invoices = frappe.db.sql(query, as_dict=1)

    modify_records(invoices)
    print(invoices)
    return invoices

def modify_records(invoices):
    indexes = []

    for idx, value in enumerate(invoices):
       if idx + 1 < len(invoices):
            if "item_code" in invoices[idx] and invoices[idx].item_code != invoices[idx + 1].item_code:
                indexes.append(idx + 1)



    for i in indexes:
        invoices.insert(i, {})
