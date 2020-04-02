# Copyright (c) 2013, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from .other_methods import *
def execute(filters=None):
	columns, data = [], []

	get_columns(columns)
	invoices = get_invoices(filters, data)
	return columns, data
