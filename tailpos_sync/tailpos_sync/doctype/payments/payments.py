# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import uuid

class Payments(Document):

	def autoname(self):
		if not self.id:
			self.id = 'Payment/' + str(uuid.uuid4())
		self.name = self.id
	def validate(self):
		if self.date_updated == None:
			print("sdadasdasd")
			try:
				print("sjhgdjakshdkashdkashdkjahsdkjh")
				self.date_updated = self.modified
			except Exception:
				print("jhsdj")
				print(frappe.get_traceback())