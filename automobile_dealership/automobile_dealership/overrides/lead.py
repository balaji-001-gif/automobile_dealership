import frappe
from erpnext.crm.doctype.lead.lead import Lead

class CustomLead(Lead):

    def after_insert(self):
        super().after_insert()
        self.assign_to_sales_consultant()
        self.send_whatsapp_acknowledgement()

    def assign_to_sales_consultant(self):
        # Round-robin assignment to available consultants
        consultants = frappe.get_all(
            "User",
            filters={"role_profile_name": "Sales Consultant", "enabled": 1},
            fields=["name"],
        )
        if not consultants:
            return

        # Simple round-robin using lead count
        consultant_loads = []
        for c in consultants:
            count = frappe.db.count("Lead", {"lead_owner": c.name, "status": "Open"})
            consultant_loads.append((c.name, count))

        assigned = min(consultant_loads, key=lambda x: x[1])[0]
        self.db_set("lead_owner", assigned)
        frappe.share.add("Lead", self.name, assigned, write=1, notify=1)

    def send_whatsapp_acknowledgement(self):
        if self.mobile_no:
            from automobile_dealership.automobile_dealership.api.whatsapp import send_message
            send_message(
                phone=self.mobile_no,
                template="lead_acknowledgement",
                params={
                    "customer_name": self.lead_name,
                    "model": self.get("custom_interested_model", ""),
                    "dealership_name": frappe.db.get_single_value(
                        "Automobile Dealership Settings", "dealership_name"
                    ),
                },
            )
