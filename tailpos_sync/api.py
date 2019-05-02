# ---
# Functions used by TailOrder
# ---
import frappe


@frappe.whitelist(allow_guest=True)
def fetch_items():
    items = []
    use_price_list = frappe.db.get_single_value('Tail Settings', 'use_price_list')

    if use_price_list:
        items = get_items_with_price_list_rate()
    else:
        items = frappe.get_all('Item', filters={'in_tailpos': 1}, fields=['name', 'item_name', 'category', 'standard_rate'])

    return post_process(items)


@frappe.whitelist(allow_guest=True)
def fetch_categories():
    categories = frappe.get_all('Categories', fields=['name'])
    return categories


def get_items_with_price_list_rate():
    pos_profile = frappe.db.get_single_value('Tail Settings', 'pos_profile')
    price_list = frappe.db.get_value('POS Profile', pos_profile, 'selling_price_list')

    items = frappe.db.sql("""SELECT `tabItem`.name, `tabItem`.category, `tabItem`.item_name, `tabItem Price`.price_list_rate as standard_rate FROM `tabItem` INNER JOIN `tabItem Price` ON `tabItem`.name = `tabItem Price`.item_code WHERE `tabItem`.in_tailpos = 1 AND `tabItem Price`.price_list=%s""", price_list, as_dict=True)

    return items


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
