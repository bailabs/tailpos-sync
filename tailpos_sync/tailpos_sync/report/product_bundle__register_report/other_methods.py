import frappe



def get_columns(columns):
    columns.append({"fieldname": "invoice_date", "label": "Invoice Date", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "invoice_number", "label": "Invoice Number", "fieldtype": "Link", "options": "Sales Invoice", "width": 150, })
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
    columns.append({"fieldname": "packed_items", "label": "Packed Items", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_item_code", "label": "Item Code", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_item_name", "label": "Item Name", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_qty", "label": "Qty", "fieldtype": "Float", "width": 150, "precision" : 2})
    columns.append({"fieldname": "packed_uom", "label": "UOM", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "packed_valuation_rate", "label":"Valuation Rate", "fieldtype": "Float", "width": 150, "precision" : 2})
    columns.append({"fieldname": "warehouse", "label":"Warehouse", "fieldtype": "Data", "width": 150})

def get_invoices(filters, data):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    print(from_date)
    print(to_date)

    query = """ 
        SELECT 
          SI.name as name, 
          SI.posting_date as posting_date, 
          R.receiptnumber as receiptnumber,
          R.date as date,
          R.deviceid as deviceid
          
        FROM `tabSales Invoice` AS SI
        INNER JOIN `tabReceipts` AS R ON SI.name = R.reference_invoice
        WHERE SI.posting_date BETWEEN '{0}' AND '{1}' ORDER BY SI.name
        
    """.format(from_date,to_date)

    invoices = frappe.db.sql(query, as_dict=1)

    modify_records(invoices, data)
    return invoices

def modify_records(invoices, data):

    for idx, value in enumerate(invoices):
        total = {
            "qty": "Total",
            "rate": 0,
            "amount": 0,
            "packed_valuation_rate": 0,
        }
        sales_invoice_item = frappe.db.sql(""" SELECT * FROM `tabSales Invoice Item` WHERE parent=%s """, value.name, as_dict=True)
        device = frappe.db.sql(""" SELECT * FROM `tabDevice`  WHERE name=%s""",value.deviceid, as_dict=True)
        obj = {
            "invoice_date": value.posting_date,
            "invoice_number": value.name,
            "receipt_no": value.receiptnumber,
            "receipt_date": value.date,
            "packed_items": "",
        }
        if len(device) > 0:
            pos_profile = frappe.db.sql(""" SELECT * FROM `tabPOS Profile`  WHERE name=%s""", device[0].pos_profile, as_dict=True)
            if len(pos_profile) > 0:
                obj['cost_center'] = pos_profile[0].cost_center

            obj['pos_profile'] = device[0].pos_profile
            obj['store_id'] = device[0].name


        for idxx, i in enumerate(sales_invoice_item):
            if idxx == 0:
                obj['item_code'] = i.item_code
                obj['item_name'] = i.item_name
                obj['qty'] = i.qty
                obj['rate'] = i.rate
                obj['amount'] = i.amount
            else:
                obj = {
                    "item_code": i.item_code,
                    "item_name": i.item_name,
                    "qty": i.qty,
                    "rate": i.rate,
                    "amount": i.amount,
                }
            total["rate"] += i.rate
            total["amount"] += i.amount
            packed_items = frappe.db.sql(""" SELECT * FROM `tabPacked Item` WHERE parent_item=%s and parent=%s """, (i.item_code, value.name) , as_dict=True)
            for idxxx,ii in enumerate(packed_items):
                if idxxx == 0:
                    obj['packed_item_code'] = ii.item_code
                    obj['packed_item_name'] = ii.item_name
                    obj['packed_qty'] = ii.qty
                    obj['packed_uom'] = ii.uom
                    obj['warehouse'] = ii.warehouse
                else:
                    obj = {
                        "packed_item_code": ii.item_code,
                        "packed_item_name": ii.item_name,
                        "packed_qty": ii.qty,
                        "packed_uom": ii.uom,
                        "warehouse": ii.warehouse,
                    }
                valuation_rate = frappe.db.sql(""" SELECT * FROM tabItem WHERE name=%s""", ii.item_code, as_dict=True)
                if len(valuation_rate) > 0:
                    obj['packed_valuation_rate'] = valuation_rate[0].valuation_rate
                    total["packed_valuation_rate"] += valuation_rate[0].valuation_rate
                    data.append(obj)
            data.append(obj)
        data.append(total)
