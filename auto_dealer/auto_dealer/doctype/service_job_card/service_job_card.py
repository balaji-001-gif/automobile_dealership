import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_hours

class ServiceJobCard(Document):

    def validate(self):
        self.set_customer_from_vehicle()
        self.calculate_estimated_cost()
        self.validate_technician_availability()

    def set_customer_from_vehicle(self):
        if self.vehicle and not self.customer:
            customer = frappe.db.get_value("Vehicle", self.vehicle, "customer")
            if customer:
                self.customer = customer

    def calculate_estimated_cost(self):
        labour_total = sum([row.amount for row in self.get("labour_items", [])])
        parts_total = sum([row.amount for row in self.get("parts_items", [])])
        self.estimated_labour_cost = labour_total
        self.estimated_parts_cost = parts_total
        self.estimated_total = labour_total + parts_total

    def validate_technician_availability(self):
        if self.technician:
            active_jobs = frappe.db.count("Service Job Card", {
                "technician": self.technician,
                "status": ["in", ["Open", "Work in Progress"]],
                "name": ["!=", self.name],
            })
            max_jobs = frappe.db.get_value("Employee", self.technician, "custom_max_concurrent_jobs") or 3
            if active_jobs >= max_jobs:
                frappe.msgprint(
                    f"Technician {self.technician} already has {active_jobs} active jobs.",
                    indicator="orange",
                    alert=True,
                )

    def on_submit(self):
        self.create_purchase_request_for_parts()
        self.notify_customer_job_started()

    def create_purchase_request_for_parts(self):
        for part in self.get("parts_items", []):
            actual_qty = frappe.db.get_value(
                "Bin",
                {"item_code": part.item_code, "warehouse": self.service_warehouse},
                "actual_qty",
            ) or 0

            if actual_qty < part.qty:
                mr = frappe.new_doc("Material Request")
                mr.material_request_type = "Purchase"
                mr.append("items", {
                    "item_code": part.item_code,
                    "qty": part.qty - actual_qty,
                    "uom": part.uom,
                    "warehouse": self.service_warehouse,
                })
                mr.insert(ignore_permissions=True)

    def notify_customer_job_started(self):
        from auto_dealer.api.whatsapp import send_message
        if self.customer_mobile:
            send_message(
                phone=self.customer_mobile,
                template="service_started",
                params={
                    "name": self.customer_name,
                    "job_card": self.name,
                    "vehicle": self.vehicle,
                    "advisor": self.service_advisor,
                },
            )

    @frappe.whitelist()
    def mark_complete(self):
        self.db_set("status", "Completed")
        self.db_set("actual_completion_time", now_datetime())
        self.calculate_actual_hours()
        self.create_service_invoice()
        self.notify_customer_ready()

    def calculate_actual_hours(self):
        if self.start_time and self.actual_completion_time:
            hours = time_diff_in_hours(self.actual_completion_time, self.start_time)
            self.db_set("actual_labour_hours", round(hours, 2))

    def create_service_invoice(self):
        si = frappe.new_doc("Sales Invoice")
        si.customer = self.customer
        si.posting_date = frappe.utils.today()

        for labour in self.get("labour_items", []):
            si.append("items", {
                "item_code": labour.service_type,
                "item_name": labour.description,
                "qty": labour.hours,
                "rate": labour.rate,
                "uom": "Hour",
            })

        for part in self.get("parts_items", []):
            si.append("items", {
                "item_code": part.item_code,
                "qty": part.qty,
                "rate": part.rate,
                "uom": part.uom,
            })

        si.insert(ignore_permissions=True)
        self.db_set("service_invoice", si.name)
        return si.name

    def notify_customer_ready(self):
        from auto_dealer.api.whatsapp import send_message
        if self.customer_mobile:
            send_message(
                phone=self.customer_mobile,
                template="vehicle_ready",
                params={
                    "name": self.customer_name,
                    "vehicle": self.vehicle,
                    "invoice": self.service_invoice,
                    "amount": self.final_total,
                },
            )
