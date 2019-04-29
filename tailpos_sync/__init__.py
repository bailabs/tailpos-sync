# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

__version__ = '1.3.3'


@frappe.whitelist()
def sync():
    hash = ''

    item_hash = frappe.db.get_single_value('Revision Hashes', 'item_hash')

    if hash == item_hash:
        return {'uptodate': 1}
    else:
        return {
            'items': frappe.get_all('Item', fields=['name', 'standard_rate'])
        }
