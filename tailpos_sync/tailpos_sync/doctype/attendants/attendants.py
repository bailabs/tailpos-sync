# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class Attendants(Document):
	def autoname(self):
		self.name = self.user_name + "-" + self.role

	def validate(self):
		if self.pin_code is not None:
			length = len(self.pin_code)

			if int(length) != 4:
				frappe.throw(_("PIN Code should contain 4 numbers only."))

			try:
				pin_code = int(self.pin_code)
			except:
				frappe.throw(_("PIN Code should be a number."))

		if self.date_updated is None:
			try:
				self.date_updated = self.modified
			except Exception:
				print(frappe.get_traceback())
