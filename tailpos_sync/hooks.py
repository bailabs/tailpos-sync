# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "tailpos_sync"
app_title = "TailPOS Sync"
app_publisher = "Bai Web and Mobile Lab"
app_description = "TailPOS ERPNext Sync"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hello@bai.ph"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tailpos_erpnext/css/tailpos_erpnext.css"
# app_include_js = "/assets/tailpos_erpnext/js/tailpos_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/tailpos_erpnext/css/tailpos_erpnext.css"
# web_include_js = "/assets/tailpos_erpnext/js/tailpos_erpnext.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "tailpos_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "tailpos_erpnext.install.before_install"
# after_install = "tailpos_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tailpos_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        "after_insert": "tailpos_sync.events.add_role",
    },
    "Item": {
        "validate": "tailpos_sync.utils.save_item",
        "before_save": "tailpos_sync.utils.set_item_uuid"
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "* * * * *": [
    #     "tailpos_erpnext.tasks.sync_couchdb"
    # ],
    # "all": [
    #     "tailpos_erpnext.tasks.sync_couchdb"
    # ],
    # "daily": [
    # 	"tailpos_erpnext.tasks.daily"
    # ],
    # "hourly": [
    # 	"tailpos_erpnext.tasks.hourly"
    # ],
    # "weekly": [
    # 	"tailpos_erpnext.tasks.weekly"
    # ]
    # "monthly": [
    # 	"tailpos_erpnext.tasks.monthly"
    # ]
}

# Testing
# -------

# before_tests = "tailpos_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tailpos_erpnext.event.get_events"
# }

fixtures = [
    {"dt": "Custom Field", "filters": [["dt", "in", ("Item", "Customer", "Deleted Document")]]},
]
