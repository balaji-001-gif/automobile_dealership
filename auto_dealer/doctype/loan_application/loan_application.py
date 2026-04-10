import frappe
from frappe.model.document import Document

class LoanApplication(Document):

    def validate(self):
        self.calculate_emi()

    def calculate_emi(self):
        # Standard EMI calculation: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        if self.loan_amount and self.interest_rate and self.tenure_months:
            p = self.loan_amount
            r = (self.interest_rate / 100) / 12
            n = self.tenure_months
            if r > 0:
                emi = p * r * ((1 + r) ** (n)) / (((1 + r) ** (n)) - 1)
                self.emi_amount = round(emi, 2)
                self.total_payable = round(emi * n, 2)
                self.total_interest = round(self.total_payable - p, 2)

    def on_submit(self):
        self.submit_to_bank_portal()

    def submit_to_bank_portal(self):
        # Integrate with bank DSA API
        from auto_dealer.api.loan_dsa import submit_application
        result = submit_application(self)
        if result.get("status") == "success":
            self.db_set("bank_reference_number", result.get("ref_no"))
            self.db_set("application_status", "Submitted to Bank")
        else:
            frappe.log_error(str(result), "Loan Application Submission Failed")

@frappe.whitelist()
def get_eligible_banks(vehicle_name, customer_name):
    vehicle = frappe.get_doc("Vehicle", vehicle_name)
    customer = frappe.get_doc("Customer", customer_name)

    settings = frappe.get_single("Auto Dealer Settings")
    banks = frappe.get_all("Empanelled Bank", fields=["bank_name", "max_ltv", "min_rate"])

    eligible = []
    for bank in banks:
        ltv_eligible = vehicle.ex_showroom_price * (bank.max_ltv / 100)
        eligible.append({
            "bank": bank.bank_name,
            "max_loan": ltv_eligible,
            "interest_rate": bank.min_rate,
        })
    return eligible
