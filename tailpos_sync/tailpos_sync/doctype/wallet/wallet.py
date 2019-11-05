# -*- coding: utf-8 -*-
# Copyright (c) 2019, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tailpos_sync.utils import set_doc_id

class Wallet(Document):
	def autoname(self):
		self.name = self.customer + "/" + self.wallet_card_number

	def validate(self):
		set_doc_id(self)
		customer = frappe.get_doc("Customer", self.customer)
		for i in customer.credit_limits:
			if i.company == self.company:
				self.credit_limit = i.credit_limit