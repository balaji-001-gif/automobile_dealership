import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today

class Vehicle(Document):

    def before_save(self):
        self.calculate_days_in_stock()
        self.validate_vin()

    def calculate_days_in_stock(self):
        if self.oem_invoice_date:
            self.days_in_stock = date_diff(today(), self.oem_invoice_date)

    def validate_vin(self):
        if self.vin_number and len(self.vin_number) != 17:
            frappe.throw("VIN Number must be exactly 17 characters.")

    def on_update(self):
        if self.status == "Sold":
            self.update_inventory_ledger()

    def update_inventory_ledger(self):
        # Create stock movement entry when vehicle is marked sold
        frappe.db.set_value("Vehicle", self.name, "status", "Sold")

    @frappe.whitelist()
    def get_valuation(self):
        # Return on-road price breakdown
        return {
            "ex_showroom": self.ex_showroom_price,
            "registration": self.get_registration_charges(),
            "insurance": self.get_insurance_estimate(),
            "accessories": self.get_accessories_total(),
            "on_road_total": self.on_road_price,
        }

    def get_registration_charges(self):
        # Placeholder — integrate with RTO fee schedule
        return self.ex_showroom_price * 0.08

    def get_insurance_estimate(self):
        return self.ex_showroom_price * 0.025

    def get_accessories_total(self):
        return sum([row.amount for row in self.get("features", [])])
