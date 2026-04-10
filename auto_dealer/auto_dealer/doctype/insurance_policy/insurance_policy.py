import frappe
from frappe.model.document import Document
from frappe.utils import add_years, today, date_diff

class InsurancePolicy(Document):

    def validate(self):
        self.set_expiry_date()
        self.calculate_renewal_due()

    def set_expiry_date(self):
        if self.policy_start_date and not self.policy_expiry_date:
            self.policy_expiry_date = add_years(self.policy_start_date, 1)

    def calculate_renewal_due(self):
        if self.policy_expiry_date:
            days_to_expiry = date_diff(self.policy_expiry_date, today())
            self.days_to_renewal = days_to_expiry

    def before_submit(self):
        self.status = "Active"

    @frappe.whitelist()
    def get_renewal_quote(self):
        from auto_dealer.api.insurance import get_renewal_quote
        return get_renewal_quote(self.policy_number, self.insurer)
