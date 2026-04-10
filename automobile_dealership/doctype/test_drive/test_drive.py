import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime

class TestDrive(Document):

    def validate(self):
        self.validate_vehicle_availability()
        self.validate_slot_conflict()
        self.validate_license()

    def validate_vehicle_availability(self):
        vehicle = frappe.get_doc("Vehicle", self.vehicle)
        if vehicle.status not in ["Available", "Demo"]:
            frappe.throw(f"Vehicle {self.vehicle} is not available for test drive.")

    def validate_slot_conflict(self):
        conflict = frappe.db.exists("Test Drive", {
            "vehicle": self.vehicle,
            "scheduled_date": self.scheduled_date,
            "scheduled_time": self.scheduled_time,
            "status": ["not in", ["Cancelled", "Completed"]],
            "name": ["!=", self.name],
        })
        if conflict:
            frappe.throw(
                f"A test drive for {self.vehicle} is already scheduled at this time."
            )

    def validate_license(self):
        if not self.driving_license_number:
            frappe.throw("Driving license number is mandatory for test drive.")

    def on_submit(self):
        self.update_vehicle_status_to_demo()
        self.send_confirmation()

    def update_vehicle_status_to_demo(self):
        frappe.db.set_value("Vehicle", self.vehicle, "status", "Demo")

    def send_confirmation(self):
        from automobile_dealership.api.whatsapp import send_message
        if self.customer_mobile:
            send_message(
                phone=self.customer_mobile,
                template="test_drive_confirmation",
                params={
                    "name": self.customer_name,
                    "vehicle": f"{self.make} {self.model}",
                    "date": self.scheduled_date,
                    "time": self.scheduled_time,
                },
            )

    def on_complete(self):
        # Called when test drive is marked completed
        frappe.db.set_value("Vehicle", self.vehicle, "status", "Available")
        self.create_follow_up_activity()

    def create_follow_up_activity(self):
        frappe.get_doc({
            "doctype": "Activity",
            "subject": f"Follow up after test drive — {self.vehicle}",
            "activity_type": "Phone",
            "reference_doctype": "Lead",
            "reference_docname": self.lead,
            "due_date": frappe.utils.add_days(frappe.utils.today(), 1),
            "assigned_to": self.sales_consultant,
        }).insert(ignore_permissions=True)
