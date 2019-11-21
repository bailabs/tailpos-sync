# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tailpos_sync.utils import set_date_updated

import uuid


class Payments(Document):
	def autoname(self):
		if not self.id:
			self.id = 'Payment/' + str(uuid.uuid4())
		self.name = self.id

	def validate(self):
		set_date_updated(self)
		try:
			self.compute_receipt_total()
		except:
			print(frappe.get_traceback())
	def compute_receipt_total(self):
		receipt_total = 0
		for i in self.payment_types:
			receipt_total += i.amount
		print("RECEEEEIPT")
		print(frappe.db.sql(""" SELECT * FROM `tabReceipts` WHERE name=%s """, self.receipt))
		frappe.db.sql(""" UPDATE `tabReceipts` SET total_amount=%s WHERE name=%s """,(receipt_total,self.receipt))
