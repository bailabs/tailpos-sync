# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from tailpos_sync.utils import set_doc_id, set_date_updated


class Discounts(Document):
    def autoname(self):
        self.name = self.description

    def validate(self):
        set_doc_id(self)
        set_date_updated(self)
        _set_percentagetype(self)


def _set_percentagetype(doc):
    discount_type = {
        'Percentage': 'percentage',
        'Fix Discount': 'fixDiscount'
    }
    doc.percentagetype = discount_type[doc.type]
