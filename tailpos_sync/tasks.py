import frappe
from datetime import datetime, timedelta


# date format
def get_sales(str_date):
    sql = frappe.db.sql("SELECT sum(total_amount), count(*) FROM tabReceipts WHERE date ='{0}'".format(str_date))
    total_sales = '{:20,.2f}'.format(sql[0][0]).strip()
    total_count = sql[0][1]

    message = 'Sales Summary \nDate: {0} \nTotal Sales: P{1} \nTransactions: {2}'.format(str_date, total_sales, total_count)


def send_sales():
    get_sales((datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d'))
