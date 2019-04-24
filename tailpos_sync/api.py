# ---
# Functions used by TailOrder
# ---
import frappe


@frappe.whitelist(allow_guest=True)
def fetch_items():
    items = frappe.get_all('Item', filters={'in_tailpos': 1}, fields=['name', 'standard_rate', 'category'])
    return post_process(items)


@frappe.whitelist(allow_guest=True)
def fetch_categories():
    categories = frappe.get_all('Categories', fields=['name'])
    return categories


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
