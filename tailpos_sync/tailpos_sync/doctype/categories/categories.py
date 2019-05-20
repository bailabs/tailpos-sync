# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import uuid


class Categories(Document):
    def autoname(self):
        self.name = self.description

    def validate(self):
        if self.date_updated is None:
            self.date_updated = self.modified
        if not self.id:
            self.id = str(uuid.uuid4())
