# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class ReceiptsClosingVoucher(Document):
	def before_submit(self):
		sales_invoice = frappe.get_doc({
			'doctype': 'Sales Invoice',
			'customer': 'Guest',
			'pos_profile': 'Default POS Profile',
			'posting_date': self.posting_date,
			'due_date': self.posting_date,
			'update_stock': 1,
			'is_pos': 1
		})

		total_amount = 0

		for receipt in self.receipts:
			lines = get_receipt_lines_by_receipt(receipt.receipt)

			for line in lines:
				item = frappe.get_doc('Receipts Item', line.name)
				sales_invoice.append('items', {
					'item_code': item.item_name,
					'item_name': item.item_name,
					'uom': item.sold_by,
					'rate': item.price,
					'qty': item.qty,
				})

			total_amount = total_amount + receipt.amount

		sales_invoice.append('payments', {
			'mode_of_payment': 'Cash',
			'amount': total_amount,
			'account': 'Cash - TOC',
			'type': 'Cash'
		})

		sales_invoice = sales_invoice.insert()
		sales_invoice.submit()
		self.generated_invoice = sales_invoice.name

	def generate(self):
		receipts = get_receipts_by_range(self.opening_date, self.closing_date)

		self.receipts = []
		expected_sales = 0

		for receipt in receipts:
			expected_sales = expected_sales + float(receipt.total_amount)
			self.append('receipts', {
				'receipt': receipt.name,
				'amount': receipt.total_amount
			})

		self.expected_sales = expected_sales


def get_receipts_by_range(start, end):
	return frappe.db.sql("""SELECT name, total_amount FROM `tabReceipts` WHERE DATE(date) BETWEEN %s AND %s""", (start, end), as_dict=1)


def get_receipt_lines_by_receipt(receipt):
	return frappe.get_all('Receipts Item', filters={'parent': receipt})
