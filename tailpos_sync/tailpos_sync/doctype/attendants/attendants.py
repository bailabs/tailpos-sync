# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document


class Attendants(Document):
	def autoname(self):
		self.name = self.user_name + "-" + self.role

	def validate(self):
		_validate_pin_code(self)
		_set_date_updated(self)


def _validate_pin_code(doc):
	pin_code_length = len(doc.pin_code)

	if pin_code_length != 4:
		frappe.throw(_('PIN should contain 4 numbers.'))

	if not doc.pin_code.isdigit():
		frappe.throw(_('PIN should only be numbers.'))


def _set_date_updated(doc):
	if not doc.date_updated:
		doc.date_updated = doc.modified
