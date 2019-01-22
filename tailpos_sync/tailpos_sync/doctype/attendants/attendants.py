# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import uuid
class Attendants(Document):
	def autoname(self):
		self.name = self.user_name + "-" + self.role

	def after_insert(self):

		if not self.from_couchdb:

			skeleton_doc = {
				"_id": self.id,
				"user_name": self.user_name,
				"pin_code": self.pin_code,
				"role": self.role
			}

	def validate(self):
		# self.syncstatus = "false"
		if self.pin_code != None:
			length = len(self.pin_code)

			if (int(length) != 4):
				frappe.throw(_("PIN Code should contain 4 numbers only."))

			try:
				pin_code = int(self.pin_code)
			except:
				frappe.throw(_("PIN Code should be a number."))
		if self.date_updated == None:
			try:
				self.date_updated = self.modified
			except Exception:
				print(frappe.get_traceback())
