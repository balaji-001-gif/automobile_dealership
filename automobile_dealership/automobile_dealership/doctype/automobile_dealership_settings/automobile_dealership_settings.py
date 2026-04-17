import frappe
from frappe.model.document import Document

class AutomobileDealershipSettings(Document):
    def validate(self):
        self.validate_whatsapp_config()

    def validate_whatsapp_config(self):
        if self.whatsapp_enabled and not self.whatsapp_api_key:
            frappe.throw("WhatsApp API Key is required when WhatsApp is enabled.")
