import frappe
import requests

TEMPLATES = {
    "lead_acknowledgement": {
        "name": "lead_ack_v1",
        "language": "en",
        "components": ["customer_name", "model", "dealership_name"],
    },
    "test_drive_confirmation": {
        "name": "test_drive_confirm_v1",
        "language": "en",
        "components": ["name", "vehicle", "date", "time"],
    },
    "service_started": {
        "name": "service_started_v1",
        "language": "en",
        "components": ["name", "job_card", "vehicle", "advisor"],
    },
    "vehicle_ready": {
        "name": "vehicle_ready_v1",
        "language": "en",
        "components": ["name", "vehicle", "invoice", "amount"],
    },
    "amc_renewal_reminder": {
        "name": "amc_renewal_v1",
        "language": "en",
        "components": ["vehicle", "expiry_date"],
    },
    "insurance_renewal": {
        "name": "insurance_renewal_v1",
        "language": "en",
        "components": ["vehicle", "policy_number", "expiry_date"],
    },
}

def send_message(phone, template, params):
    settings = frappe.get_single("Auto Dealer Settings")

    if not settings.whatsapp_enabled:
        frappe.logger().info(f"WhatsApp disabled. Would send {template} to {phone}")
        return

    template_config = TEMPLATES.get(template)
    if not template_config:
        frappe.log_error(f"Unknown template: {template}", "WhatsApp")
        return

    phone = phone.replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+91" + phone.lstrip("0")

    components = []
    for key in template_config["components"]:
        components.append({
            "type": "text",
            "text": str(params.get(key, "")),
        })

    payload = {
        "countryCode": "+91",
        "phoneNumber": phone.replace("+91", ""),
        "type": "Template",
        "template": {
            "name": template_config["name"],
            "languageCode": template_config["language"],
            "bodyValues": components,
        },
    }

    try:
        response = requests.post(
            settings.whatsapp_api_url,
            json=payload,
            headers={
                "api-key": settings.whatsapp_api_key,
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
        log_whatsapp_message(phone, template, "Sent")
        return response.json()
    except Exception as e:
        frappe.log_error(str(e), f"WhatsApp Send Error — {template}")
        log_whatsapp_message(phone, template, "Failed", str(e))

def log_whatsapp_message(phone, template, status, error=None):
    frappe.get_doc({
        "doctype": "WhatsApp Log",
        "phone": phone,
        "template": template,
        "status": status,
        "error": error,
        "timestamp": frappe.utils.now_datetime(),
    }).insert(ignore_permissions=True)
