# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from tailpos_sync.utils import set_date_updated, set_doc_id


class Attendants(Document):
	def autoname(self):
		self.name = self.user_name + "-" + self.role

	def validate(self):
		_validate_pin_code(self)
		set_doc_id(self)
		set_date_updated(self)


def _validate_pin_code(doc):
	pin_code_length = len(doc.pin_code)

	if pin_code_length != 4:
		frappe.throw(_('PIN should contain 4 numbers.'))

	if not doc.pin_code.isdigit():
		frappe.throw(_('PIN should only be numbers.'))
