import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class VehicleSale(Document):

    def validate(self):
        self.validate_vehicle_availability()
        self.calculate_totals()
        self.set_customer_details()

    def validate_vehicle_availability(self):
        vehicle_status = frappe.db.get_value("Vehicle", self.vehicle, "status")
        if vehicle_status not in ["Available", "Booked"]:
            frappe.throw(
                f"Vehicle {self.vehicle} is not available for sale. Current status: {vehicle_status}"
            )

    def calculate_totals(self):
        self.subtotal = (
            (self.ex_showroom_price or 0) +
            (self.registration_charges or 0) +
            (self.insurance_premium or 0) +
            (self.accessories_total or 0) +
            (self.handling_charges or 0)
        )
        self.discount_amount = self.subtotal * (self.discount_percent or 0) / 100
        self.grand_total = self.subtotal - self.discount_amount
        self.balance_amount = self.grand_total - (self.advance_received or 0)

    def set_customer_details(self):
        if self.customer:
            customer = frappe.get_doc("Customer", self.customer)
            self.customer_name = customer.customer_name
            self.customer_mobile = customer.mobile_no

    def on_submit(self):
        self.update_vehicle_status()
        self.create_sales_invoice()
        self.create_crm_activity()
        self.trigger_delivery_checklist()

    def update_vehicle_status(self):
        frappe.db.set_value("Vehicle", self.vehicle, "status", "Sold")
        frappe.db.set_value("Vehicle", self.vehicle, "customer", self.customer)

    def create_sales_invoice(self):
        si = frappe.new_doc("Sales Invoice")
        si.customer = self.customer
        si.set_posting_time = 1
        si.posting_date = nowdate()
        si.append("items", {
            "item_code": self.vehicle,
            "item_name": f"{self.make} {self.model} {self.variant}",
            "qty": 1,
            "rate": self.grand_total,
            "uom": "Nos",
        })
        si.insert(ignore_permissions=True)
        self.sales_invoice = si.name
        frappe.db.set_value("Vehicle Sale", self.name, "sales_invoice", si.name)

    def create_crm_activity(self):
        frappe.get_doc({
            "doctype": "CRM Activity",
            "activity_type": "Vehicle Sold",
            "customer": self.customer,
            "vehicle": self.vehicle,
            "reference_doctype": "Vehicle Sale",
            "reference_docname": self.name,
        }).insert(ignore_permissions=True)

    def trigger_delivery_checklist(self):
        frappe.get_doc({
            "doctype": "Vehicle Delivery Checklist",
            "vehicle_sale": self.name,
            "vehicle": self.vehicle,
            "customer": self.customer,
            "scheduled_date": self.delivery_date,
        }).insert(ignore_permissions=True)
