import frappe
from frappe.model.document import Document
from frappe.utils import add_years, date_diff, today, add_days

class AMCContract(Document):

    def validate(self):
        self.set_end_date()
        self.calculate_next_service_due()

    def set_end_date(self):
        if self.start_date and self.duration_years and not self.end_date:
            self.end_date = add_years(self.start_date, self.duration_years)

    def calculate_next_service_due(self):
        if self.last_service_date:
            self.next_service_due = add_days(self.last_service_date, self.service_interval_days or 90)

    @frappe.whitelist()
    def renew(self):
        new_amc = frappe.copy_doc(self)
        new_amc.start_date = add_days(self.end_date, 1)
        new_amc.end_date = add_years(new_amc.start_date, self.duration_years)
        new_amc.status = "Draft"
        new_amc.insert()
        return new_amc.name

def send_amc_renewal_reminders():
    due_contracts = frappe.get_all(
        "AMC Contract",
        filters={
            "status": "Active",
            "end_date": ["between", [today(), add_days(today(), 30)]],
        },
        fields=["name", "customer", "vehicle", "end_date", "customer_mobile"],
    )
    for contract in due_contracts:
        from auto_dealer.api.whatsapp import send_message
        if contract.customer_mobile:
            send_message(
                phone=contract.customer_mobile,
                template="amc_renewal_reminder",
                params={
                    "vehicle": contract.vehicle,
                    "expiry_date": contract.end_date,
                },
            )
