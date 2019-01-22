import frappe


def send_msg(message, recipient):
    """Send message with the recipient"""
    import requests

    sms_settings = frappe.get_doc('SMS Settings', 'SMS Settings')

    url = sms_settings.sms_gateway_url
    msgkey = sms_settings.message_parameter
    reckey = sms_settings.receiver_parameter

    payload = {
        msgkey: message,
        reckey: recipient
    }

    for param in sms_settings.parameters:
        payload.update({param.parameter: param.value})

    requests.post(url, data=payload)