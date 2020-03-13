import frappe


def get_columns(columns):
    columns.append({"fieldname": "transaction_date", "label": "Transaction Date", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "receipt_number", "label": "Receipt Number", "fieldtype": "Data", "width": 150, })
    columns.append({"fieldname": "payment_date", "label": "Payment Date", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "paid_amount", "label": "Paid Amount", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "change", "label": "Change", "fieldtype": "Data", "width": 150})


def get_more_columns(columns):
    columns.append({"fieldname": "discount_type", "label": "Discount Type", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "discount_amount", "label": "Discount Amount", "fieldtype": "Data", "width": 150})
    columns.append({"fieldname": "taxes_amount", "label": "Taxes Amount", "fieldtype": "Data", "width": 150})
    columns.append(
        {"fieldname": "total_amount_in_receipt", "label": "Total Amount in Receipt", "fieldtype": "Data", "width": 170})
    columns.append({"fieldname": "reference_invoice_number", "label": "Reference Invoice Number", "fieldtype": "Link",
                    "width": 170, "options": "Sales Invoice"})
    columns.append({"fieldname": "device_id", "label": "Device ID", "fieldtype": "Data", "width": 140})
    columns.append({"fieldname": "updated_date", "label": "Updated Date", "fieldtype": "Data", "width": 170})
    columns.append({"fieldname": "invoice_status", "label": "Invoice Status", "fieldtype": "Data", "width": 150})
    columns.append(
        {"fieldname": "total_taxes_and_charges", "label": "Total Tax and Charges", "fieldtype": "Float", "width": 150,'precision': 2})
    columns.append({"fieldname": "grand_total", "label": "Grand Total", "fieldtype": "Float", "width": 150,'precision': 2})
