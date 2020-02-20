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
		self.compute_receipt_total()
	def compute_receipt_total(self):
		receipt = frappe.db.sql(""" SELECT total_amount FROM tabReceipts WHERE name=%s """, self.receipt, as_dict=True)
		change = self.paid - receipt[0].total_amount
		self.change = change
		for i in self.payment_types:
			if i.type == "Cash":
				i.amount = i.amount - change

