# ---
# Functions used by TailOrder
# ---
import frappe
import json


@frappe.whitelist(allow_guest=True)
def fetch_items():
    try:
        data = json.loads(frappe.request.data)
    except:
        data = None

    pos_profile = None

    if data:
        pos_profile = frappe.db.get_value('Device', data['device'], 'pos_profile')

    use_price_list = frappe.db.get_single_value('Tail Settings', 'use_price_list')

    if use_price_list:
        items = get_items_with_price_list_rate(pos_profile)
    else:
        items = get_items_with_standard_rate()

    return post_process(items)


@frappe.whitelist(allow_guest=True)
def fetch_categories():
    return frappe.get_all('Categories', fields=['name'])


@frappe.whitelist(allow_guest=True)
def fetch_remarks():
    return frappe.get_all('Remarks Template', fields=['name'])


def get_items_with_price_list_rate(pos_profile=None):
    if not pos_profile:
        pos_profile = frappe.db.get_single_value('Tail Settings', 'pos_profile')

    price_list = frappe.db.get_value('POS Profile', pos_profile, 'selling_price_list')

    items = frappe.db.sql("""SELECT `tabItem`.name, `tabItem`.category, `tabItem`.item_name, `tabItem Price`.price_list_rate as standard_rate, `tabItem`.color FROM `tabItem` INNER JOIN `tabItem Price` ON `tabItem`.name = `tabItem Price`.item_code WHERE `tabItem`.in_tailpos = 1 AND `tabItem Price`.price_list=%s""", price_list, as_dict=True)

    return items


def get_items_with_standard_rate():
    filters = {'in_tailpos': 1}
    fields = ['name', 'item_name', 'category', 'standard_rate', 'color']

    return frappe.get_all('Item', filters=filters, fields=fields)


def post_process(arr_obj):
    camelized_arr = [camelized_dict(obj) for obj in arr_obj]
    return camelized_arr


def camelized_dict(dict_obj):
    new_obj = {}

    for k, v in dict_obj.items():
        k = ''.join([camelized_element(i, k_list) for i, k_list in enumerate(k.split('_'))])
        new_obj.update({k: v})

    return new_obj


def camelized_element(index, element):
    if index == 0:
        return element.lower()
    return element.capitalize()
