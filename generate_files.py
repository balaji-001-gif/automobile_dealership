import os

base_dir = "/Users/balajik/auto -dealer"

files = {
    "automobile_dealership/hooks.py": """app_name = "automobile_dealership"
app_title = "Automobile Dealership"
app_publisher = "Your Company"
app_description = "Automobile Dealership Management"
app_version = "1.0.0"
app_license = "MIT"

# Required apps
required_apps = ["frappe", "erpnext"]

# DocType overrides
override_doctype_class = {
    "Sales Order": "automobile_dealership.automobile_dealership.overrides.sales_order.CustomSalesOrder",
    "Customer": "automobile_dealership.automobile_dealership.overrides.customer.CustomCustomer",
}

# Scheduled tasks
scheduler_events = {
    "daily": [
        "automobile_dealership.automobile_dealership.tasks.send_service_reminders",
        "automobile_dealership.automobile_dealership.tasks.check_insurance_renewals",
        "automobile_dealership.automobile_dealership.tasks.check_amc_renewals",
        "automobile_dealership.automobile_dealership.tasks.oem_target_sync",
    ],
    "weekly": [
        "automobile_dealership.automobile_dealership.tasks.slow_moving_inventory_alert",
    ],
    "monthly": [
        "automobile_dealership.automobile_dealership.tasks.generate_oem_monthly_report",
    ],
}

# Document events
doc_events = {
    "Vehicle Sale": {
        "on_submit": [
            "automobile_dealership.automobile_dealership.events.vehicle_sale.on_submit",
            "automobile_dealership.automobile_dealership.events.vehicle_sale.trigger_whatsapp_confirmation",
        ],
        "on_cancel": "automobile_dealership.automobile_dealership.events.vehicle_sale.on_cancel",
    },
    "Service Job Card": {
        "on_submit": "automobile_dealership.automobile_dealership.events.service_job_card.on_submit",
        "on_update": "automobile_dealership.automobile_dealership.events.service_job_card.update_job_status",
    },
    "Customer": {
        "after_insert": "automobile_dealership.automobile_dealership.events.customer.create_crm_profile",
    },
}

# Fixtures (data to export/import with app)
fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Dealer Admin", "Sales Consultant", "Service Advisor",
        "Workshop Technician", "Finance Executive", "DMS Manager"
    ]]]},
    {"dt": "Workflow", "filters": [["document_type", "in", [
        "Vehicle Sale", "Service Job Card", "Test Drive"
    ]]]},
    {"dt": "Print Format"},
    {"dt": "Custom Field"},
    {"dt": "Property Setter"},
]

# Website context
website_context = {
    "favicon": "/assets/automobile_dealership/images/favicon.ico",
}
""",
    "automobile_dealership/modules.txt": """Automobile Dealership\n""",
    "automobile_dealership/automobile_dealership/doctype/vehicle/vehicle.json": """{
  "name": "Vehicle",
  "module": "Automobile Dealership",
  "doctype": "DocType",
  "is_submittable": 0,
  "track_changes": 1,
  "fields": [
    {"fieldname": "vin_number", "label": "VIN Number", "fieldtype": "Data", "reqd": 1, "unique": 1},
    {"fieldname": "registration_number", "label": "Registration Number", "fieldtype": "Data"},
    {"fieldname": "make", "label": "Make", "fieldtype": "Link", "options": "Vehicle Make", "reqd": 1},
    {"fieldname": "model", "label": "Model", "fieldtype": "Link", "options": "Vehicle Model", "reqd": 1},
    {"fieldname": "variant", "label": "Variant", "fieldtype": "Data"},
    {"fieldname": "year_of_manufacture", "label": "Year", "fieldtype": "Int", "reqd": 1},
    {"fieldname": "color", "label": "Color", "fieldtype": "Link", "options": "Vehicle Color"},
    {"fieldname": "fuel_type", "label": "Fuel Type", "fieldtype": "Select",
      "options": "Petrol\\nDiesel\\nCNG\\nElectric\\nHybrid"},
    {"fieldname": "transmission", "label": "Transmission", "fieldtype": "Select",
      "options": "Manual\\nAutomatic\\nAMT\\nDCT\\nCVT"},
    {"fieldname": "vehicle_type", "label": "Vehicle Type", "fieldtype": "Select",
      "options": "New\\nUsed\\nDemo\\nCertified Pre-Owned"},
    {"fieldname": "odometer_reading", "label": "Odometer (km)", "fieldtype": "Int"},
    {"fieldname": "engine_number", "label": "Engine Number", "fieldtype": "Data"},
    {"fieldname": "chassis_number", "label": "Chassis Number", "fieldtype": "Data"},
    {"fieldname": "cost_price", "label": "Cost Price", "fieldtype": "Currency"},
    {"fieldname": "ex_showroom_price", "label": "Ex-Showroom Price", "fieldtype": "Currency"},
    {"fieldname": "on_road_price", "label": "On-Road Price", "fieldtype": "Currency"},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select",
      "options": "Available\\nBooked\\nSold\\nIn Service\\nDemo\\nTransit"},
    {"fieldname": "location", "label": "Showroom Location", "fieldtype": "Link", "options": "Warehouse"},
    {"fieldname": "oem_invoice_number", "label": "OEM Invoice No", "fieldtype": "Data"},
    {"fieldname": "oem_invoice_date", "label": "OEM Invoice Date", "fieldtype": "Date"},
    {"fieldname": "days_in_stock", "label": "Days in Stock", "fieldtype": "Int", "read_only": 1},
    {"fieldname": "image", "label": "Vehicle Image", "fieldtype": "Attach Image"},
    {"fieldname": "features_section", "label": "Features", "fieldtype": "Section Break"},
    {"fieldname": "features", "label": "Features", "fieldtype": "Table",
      "options": "Vehicle Feature Item"},
    {"fieldname": "documents_section", "label": "Documents", "fieldtype": "Section Break"},
    {"fieldname": "rc_book", "label": "RC Book", "fieldtype": "Attach"},
    {"fieldname": "insurance_doc", "label": "Insurance Document", "fieldtype": "Attach"},
    {"fieldname": "puc_certificate", "label": "PUC Certificate", "fieldtype": "Attach"}
  ],
  "permissions": [
    {"role": "Dealer Admin", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1},
    {"role": "Sales Consultant", "read": 1, "write": 1, "create": 1},
    {"role": "DMS Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
  ]
}
""",
    "automobile_dealership/automobile_dealership/doctype/vehicle/vehicle.py": """import frappe
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
""",
    "automobile_dealership/automobile_dealership/doctype/vehicle_sale/vehicle_sale.py": """import frappe
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
""",
    "automobile_dealership/automobile_dealership/doctype/vehicle_inventory_log/vehicle_inventory_log.py": """import frappe
from frappe.model.document import Document

class VehicleInventoryLog(Document):
    pass

@frappe.whitelist()
def get_slow_moving_vehicles(days_threshold=60):
    return frappe.db.sql('''
        SELECT
            v.name,
            v.make,
            v.model,
            v.variant,
            v.color,
            v.fuel_type,
            v.vehicle_type,
            v.ex_showroom_price,
            v.days_in_stock,
            v.location,
            v.status
        FROM `tabVehicle` v
        WHERE v.status = 'Available'
          AND v.days_in_stock > %(days)s
        ORDER BY v.days_in_stock DESC
    ''', {"days": days_threshold}, as_dict=True)
""",
    "automobile_dealership/automobile_dealership/api/marketplace_sync.py": """import frappe
import requests

def sync_to_cardekho(vehicle_name):
    # Sync vehicle listing to CarDekho partner portal
    vehicle = frappe.get_doc("Vehicle", vehicle_name)
    settings = frappe.get_single("Automobile Dealership Settings")

    payload = {
        "dealer_id": settings.cardekho_dealer_id,
        "vin": vehicle.vin_number,
        "make": vehicle.make,
        "model": vehicle.model,
        "variant": vehicle.variant,
        "year": vehicle.year_of_manufacture,
        "color": vehicle.color,
        "fuel": vehicle.fuel_type,
        "transmission": vehicle.transmission,
        "price": vehicle.ex_showroom_price,
        "odometer": vehicle.odometer_reading,
        "images": [vehicle.image] if vehicle.image else [],
    }

    try:
        response = requests.post(
            settings.cardekho_api_url,
            json=payload,
            headers={"Authorization": f"Bearer {settings.cardekho_api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        frappe.logger().info(f"Vehicle {vehicle_name} synced to CarDekho")
        return {"status": "success", "listing_id": response.json().get("listing_id")}
    except Exception as e:
        frappe.log_error(str(e), "CarDekho Sync Error")
        return {"status": "error", "message": str(e)}
""",
    "automobile_dealership/automobile_dealership/patches/add_vehicle_parts_fields.py": """import frappe

def execute():
    # Add custom fields to Item doctype for auto parts
    custom_fields = {
        "Item": [
            {
                "fieldname": "is_vehicle_part",
                "label": "Is Vehicle Part",
                "fieldtype": "Check",
                "insert_after": "is_stock_item",
            },
            {
                "fieldname": "compatible_makes",
                "label": "Compatible Makes",
                "fieldtype": "Table MultiSelect",
                "options": "Vehicle Make",
                "insert_after": "is_vehicle_part",
                "depends_on": "eval:doc.is_vehicle_part",
            },
            {
                "fieldname": "part_number",
                "label": "OEM Part Number",
                "fieldtype": "Data",
                "insert_after": "compatible_makes",
                "depends_on": "eval:doc.is_vehicle_part",
            },
        ]
    }
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(custom_fields)
""",
    "automobile_dealership/automobile_dealership/overrides/lead.py": """import frappe
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
""",
    "automobile_dealership/automobile_dealership/doctype/test_drive/test_drive.py": """import frappe
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
        from automobile_dealership.automobile_dealership.api.whatsapp import send_message
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
""",
    "automobile_dealership/automobile_dealership/doctype/loan_application/loan_application.py": """import frappe
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
        from automobile_dealership.automobile_dealership.api.loan_dsa import submit_application
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

    settings = frappe.get_single("Automobile Dealership Settings")
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
""",
    "automobile_dealership/automobile_dealership/doctype/insurance_policy/insurance_policy.py": """import frappe
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
        from automobile_dealership.automobile_dealership.api.insurance import get_renewal_quote
        return get_renewal_quote(self.policy_number, self.insurer)
""",
    "automobile_dealership/automobile_dealership/setup/billing_setup.py": """import frappe

def setup_gst_accounts(company):
    gst_accounts = [
        {"account_name": "CGST Payable", "parent_account": "Duties and Taxes", "tax_rate": 14},
        {"account_name": "SGST Payable", "parent_account": "Duties and Taxes", "tax_rate": 14},
        {"account_name": "IGST Payable", "parent_account": "Duties and Taxes", "tax_rate": 28},
        {"account_name": "TCS Payable", "parent_account": "Duties and Taxes", "tax_rate": 1},
    ]

    for acc in gst_accounts:
        if not frappe.db.exists("Account", {"account_name": acc["account_name"], "company": company}):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": acc["account_name"],
                "parent_account": f"{acc['parent_account']} - {frappe.db.get_value('Company', company, 'abbr')}",
                "account_type": "Tax",
                "company": company,
            }).insert()

def create_vehicle_sale_tax_template():
    if frappe.db.exists("Sales Taxes and Charges Template", "Vehicle Sale GST 28%"):
        return

    doc = frappe.new_doc("Sales Taxes and Charges Template")
    doc.title = "Vehicle Sale GST 28%"
    doc.append("taxes", {
        "charge_type": "On Net Total",
        "account_head": "CGST Payable - AD",
        "rate": 14,
        "description": "CGST @ 14%",
    })
    doc.append("taxes", {
        "charge_type": "On Net Total",
        "account_head": "SGST Payable - AD",
        "rate": 14,
        "description": "SGST @ 14%",
    })
    doc.insert()
""",
    "automobile_dealership/automobile_dealership/doctype/service_job_card/service_job_card.py": """import frappe
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
        from automobile_dealership.automobile_dealership.api.whatsapp import send_message
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
        from automobile_dealership.automobile_dealership.api.whatsapp import send_message
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
""",
    "automobile_dealership/automobile_dealership/doctype/amc_contract/amc_contract.py": """import frappe
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
        from automobile_dealership.automobile_dealership.api.whatsapp import send_message
        if contract.customer_mobile:
            send_message(
                phone=contract.customer_mobile,
                template="amc_renewal_reminder",
                params={
                    "vehicle": contract.vehicle,
                    "expiry_date": contract.end_date,
                },
            )
""",
    "automobile_dealership/automobile_dealership/doctype/sales_incentive_rule/sales_incentive_rule.py": """import frappe
from frappe.model.document import Document

class SalesIncentiveRule(Document):
    pass

@frappe.whitelist()
def calculate_consultant_incentive(employee, month, year):
    sales = frappe.db.sql('''
        SELECT
            vs.name,
            vs.vehicle,
            vs.grand_total,
            vs.make,
            vs.model,
            vs.vehicle_type,
            vs.finance_done,
            vs.insurance_done,
            vs.accessories_total
        FROM `tabVehicle Sale` vs
        WHERE vs.sales_consultant = %(employee)s
          AND MONTH(vs.posting_date) = %(month)s
          AND YEAR(vs.posting_date) = %(year)s
          AND vs.docstatus = 1
    ''', {"employee": employee, "month": month, "year": year}, as_dict=True)

    rules = frappe.get_all(
        "Sales Incentive Rule",
        filters={"is_active": 1},
        fields=["*"],
        order_by="min_sales_count asc",
    )

    total_incentive = 0
    breakdown = []

    for sale in sales:
        vehicle_incentive = get_vehicle_incentive(sale, rules)
        total_incentive += vehicle_incentive

        if sale.finance_done:
            finance_bonus = frappe.db.get_single_value(
                "Automobile Dealership Settings", "finance_crosssell_bonus"
            ) or 500
            total_incentive += finance_bonus

        if sale.insurance_done:
            insurance_bonus = frappe.db.get_single_value(
                "Automobile Dealership Settings", "insurance_crosssell_bonus"
            ) or 300
            total_incentive += insurance_bonus

        if sale.accessories_total:
            accessories_commission = sale.accessories_total * 0.05
            total_incentive += accessories_commission

        breakdown.append({
            "sale": sale.name,
            "vehicle": sale.vehicle,
            "vehicle_incentive": vehicle_incentive,
            "finance_bonus": finance_bonus if sale.finance_done else 0,
            "insurance_bonus": insurance_bonus if sale.insurance_done else 0,
            "accessories_commission": accessories_commission if sale.accessories_total else 0,
        })

    return {
        "employee": employee,
        "month": month,
        "year": year,
        "total_sales": len(sales),
        "total_incentive": round(total_incentive, 2),
        "breakdown": breakdown,
    }

def get_vehicle_incentive(sale, rules):
    for rule in rules:
        if sale.vehicle_type == rule.vehicle_type:
            return rule.incentive_amount
    return 0
""",
    "automobile_dealership/automobile_dealership/api/attendance.py": """import frappe
from frappe.utils import today, now_datetime

@frappe.whitelist()
def mark_technician_attendance(employee, status="Present"):
    if frappe.db.exists("Attendance", {
        "employee": employee,
        "attendance_date": today(),
        "docstatus": ["!=", 2],
    }):
        frappe.throw(f"Attendance already marked for {employee} today.")

    att = frappe.new_doc("Attendance")
    att.employee = employee
    att.attendance_date = today()
    att.status = status
    att.company = frappe.defaults.get_user_default("Company")
    att.insert(ignore_permissions=True)
    att.submit()
    return att.name
""",
    "automobile_dealership/automobile_dealership/api/whatsapp.py": """import frappe
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
    settings = frappe.get_single("Automobile Dealership Settings")

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
""",
    "automobile_dealership/automobile_dealership/doctype/loyalty_account/loyalty_account.py": """import frappe
from frappe.model.document import Document

class LoyaltyAccount(Document):

    @frappe.whitelist()
    def add_points(self, points, reference_type, reference_name, remarks=""):
        self.append("transactions", {
            "transaction_date": frappe.utils.today(),
            "points": points,
            "transaction_type": "Credit",
            "reference_doctype": reference_type,
            "reference_docname": reference_name,
            "remarks": remarks,
        })
        self.total_points = (self.total_points or 0) + points
        self.save(ignore_permissions=True)

    @frappe.whitelist()
    def redeem_points(self, points, reference_name, remarks=""):
        if points > (self.total_points or 0):
            frappe.throw("Insufficient loyalty points.")
        self.append("transactions", {
            "transaction_date": frappe.utils.today(),
            "points": -points,
            "transaction_type": "Debit",
            "reference_docname": reference_name,
            "remarks": remarks,
        })
        self.total_points = (self.total_points or 0) - points
        self.save(ignore_permissions=True)
        return points * (frappe.db.get_single_value("Automobile Dealership Settings", "loyalty_point_value") or 1)
""",
    "automobile_dealership/automobile_dealership/page/dealer_dashboard/dealer_dashboard.py": """import frappe

@frappe.whitelist()
def get_dashboard_data():
    from frappe.utils import today, get_first_day, get_last_day, add_months

    today_date = today()
    month_start = get_first_day(today_date)
    month_end = get_last_day(today_date)
    prev_month_start = get_first_day(add_months(today_date, -1))
    prev_month_end = get_last_day(add_months(today_date, -1))

    return {
        "vehicles": {
            "available": frappe.db.count("Vehicle", {"status": "Available"}),
            "booked": frappe.db.count("Vehicle", {"status": "Booked"}),
            "sold_this_month": frappe.db.count("Vehicle Sale", {
                "docstatus": 1,
                "posting_date": ["between", [month_start, month_end]],
            }),
            "slow_moving": frappe.db.count("Vehicle", {
                "status": "Available",
                "days_in_stock": [">", 60],
            }),
        },
        "revenue": {
            "vehicle_sales_mtd": get_vehicle_sales_revenue(month_start, month_end),
            "service_revenue_mtd": get_service_revenue(month_start, month_end),
            "parts_revenue_mtd": get_parts_revenue(month_start, month_end),
        },
        "leads": {
            "new_today": frappe.db.count("Lead", {"creation": [">=", today_date]}),
            "open": frappe.db.count("Lead", {"status": "Open"}),
            "converted_mtd": frappe.db.count("Lead", {
                "status": "Converted",
                "modified": ["between", [month_start, month_end]],
            }),
        },
        "service": {
            "open_jobs": frappe.db.count("Service Job Card", {
                "status": ["in", ["Open", "Work in Progress"]],
            }),
            "completed_today": frappe.db.count("Service Job Card", {
                "status": "Completed",
                "modified": [">=", today_date],
            }),
            "pending_delivery": frappe.db.count("Service Job Card", {
                "status": "Completed",
                "is_delivered": 0,
            }),
        },
        "oem_targets": get_oem_target_progress(month_start, month_end),
    }

def get_vehicle_sales_revenue(start, end):
    result = frappe.db.sql('''
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabVehicle Sale`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(start)s AND %(end)s
    ''', {"start": start, "end": end})
    return result[0][0] if result else 0

def get_service_revenue(start, end):
    result = frappe.db.sql('''
        SELECT COALESCE(SUM(final_total), 0) as total
        FROM `tabService Job Card`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(start)s AND %(end)s
    ''', {"start": start, "end": end})
    return result[0][0] if result else 0

def get_parts_revenue(start, end):
    return frappe.db.sql('''
        SELECT COALESCE(SUM(si.base_grand_total), 0)
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.is_parts_invoice = 1
          AND si.posting_date BETWEEN %(start)s AND %(end)s
    ''', {"start": start, "end": end})[0][0] or 0

def get_oem_target_progress(month_start, month_end):
    target = frappe.db.get_value("OEM Target", {
        "month": frappe.utils.getdate(month_start).month,
        "year": frappe.utils.getdate(month_start).year,
    }, ["target_volume", "target_revenue"])

    if not target:
        return {"target": 0, "achieved": 0, "percent": 0}

    achieved = frappe.db.count("Vehicle Sale", {
        "docstatus": 1,
        "posting_date": ["between", [month_start, month_end]],
    })

    return {
        "target": target[0] or 0,
        "achieved": achieved,
        "percent": round((achieved / target[0]) * 100, 1) if target[0] else 0,
    }
""",
    "automobile_dealership/automobile_dealership/report/oem_monthly_report/oem_monthly_report.py": """import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 150},
        {"label": "Variant", "fieldname": "variant", "fieldtype": "Data", "width": 120},
        {"label": "Color", "fieldname": "color", "fieldtype": "Data", "width": 100},
        {"label": "Fuel Type", "fieldname": "fuel_type", "fieldtype": "Data", "width": 100},
        {"label": "Units Sold", "fieldname": "units_sold", "fieldtype": "Int", "width": 100},
        {"label": "Retail Revenue", "fieldname": "retail_revenue", "fieldtype": "Currency", "width": 150},
        {"label": "Finance Penetration %", "fieldname": "finance_pct", "fieldtype": "Percent", "width": 150},
        {"label": "Insurance Penetration %", "fieldname": "insurance_pct", "fieldtype": "Percent", "width": 160},
        {"label": "Avg Discount", "fieldname": "avg_discount", "fieldtype": "Currency", "width": 130},
    ]

def get_data(filters):
    conditions = []
    if filters.get("month"):
        conditions.append(f"MONTH(vs.posting_date) = {filters['month']}")
    if filters.get("year"):
        conditions.append(f"YEAR(vs.posting_date) = {filters['year']}")

    where_clause = "AND " + " AND ".join(conditions) if conditions else ""

    return frappe.db.sql(f'''
        SELECT
            vs.model,
            vs.variant,
            vs.color,
            vs.fuel_type,
            COUNT(*) as units_sold,
            SUM(vs.grand_total) as retail_revenue,
            ROUND(SUM(vs.finance_done) / COUNT(*) * 100, 1) as finance_pct,
            ROUND(SUM(vs.insurance_done) / COUNT(*) * 100, 1) as insurance_pct,
            ROUND(AVG(vs.discount_amount), 0) as avg_discount
        FROM `tabVehicle Sale` vs
        WHERE vs.docstatus = 1
        {where_clause}
        GROUP BY vs.model, vs.variant, vs.color, vs.fuel_type
        ORDER BY units_sold DESC
    ''', as_dict=True)
""",
    "automobile_dealership/automobile_dealership/doctype/automobile_dealership_settings/automobile_dealership_settings.py": """import frappe
from frappe.model.document import Document

class AutoDealerSettings(Document):
    def validate(self):
        self.validate_whatsapp_config()

    def validate_whatsapp_config(self):
        if self.whatsapp_enabled and not self.whatsapp_api_key:
            frappe.throw("WhatsApp API Key is required when WhatsApp is enabled.")
""",
    "automobile_dealership/automobile_dealership/api/loan_dsa.py": """import frappe
import requests

def submit_application(loan_doc):
    settings = frappe.get_single("Auto dealer Settings")

    payload = {
        "dealer_code": settings.dealer_code,
        "customer_name": loan_doc.customer_name,
        "customer_pan": loan_doc.customer_pan,
        "customer_mobile": loan_doc.customer_mobile,
        "vehicle_type": loan_doc.vehicle_type,
        "vehicle_value": loan_doc.vehicle_value,
        "loan_amount": loan_doc.loan_amount,
        "tenure_months": loan_doc.tenure_months,
        "employment_type": loan_doc.employment_type,
        "monthly_income": loan_doc.monthly_income,
    }

    try:
        response = requests.post(
            f"{settings.dsa_api_url}/applications",
            json=payload,
            headers={"Authorization": f"Bearer {settings.dsa_api_token}"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        frappe.log_error(str(e), "Loan DSA API Error")
        return {"status": "error", "message": str(e)}
""",
    "automobile_dealership/automobile_dealership/setup/roles.py": """import frappe

def create_roles():
    roles = [
        {"role_name": "Dealer Admin", "desk_access": 1},
        {"role_name": "DMS Manager", "desk_access": 1},
        {"role_name": "Sales Consultant", "desk_access": 1},
        {"role_name": "Service Advisor", "desk_access": 1},
        {"role_name": "Workshop Technician", "desk_access": 1},
        {"role_name": "Finance Executive", "desk_access": 1},
    ]

    for role in roles:
        if not frappe.db.exists("Role", role["role_name"]):
            frappe.get_doc({"doctype": "Role", **role}).insert()
""",
    "automobile_dealership/automobile_dealership/fixtures/workflow_vehicle_sale.json": """{
  "doctype": "Workflow",
  "name": "Vehicle Sale Workflow",
  "document_type": "Vehicle Sale",
  "workflow_name": "Vehicle Sale Workflow",
  "is_active": 1,
  "states": [
    {"state": "Draft", "doc_status": "0", "allow_edit": "Sales Consultant"},
    {"state": "Verified", "doc_status": "0", "allow_edit": "DMS Manager"},
    {"state": "Finance Approved", "doc_status": "0", "allow_edit": "Finance Executive"},
    {"state": "Delivery Scheduled", "doc_status": "0", "allow_edit": "DMS Manager"},
    {"state": "Delivered", "doc_status": "1", "allow_edit": "Dealer Admin"}
  ],
  "transitions": [
    {"state": "Draft", "action": "Verify", "next_state": "Verified",
     "allowed": "DMS Manager", "condition": "doc.grand_total > 0"},
    {"state": "Verified", "action": "Approve Finance", "next_state": "Finance Approved",
     "allowed": "Finance Executive"},
    {"state": "Finance Approved", "action": "Schedule Delivery", "next_state": "Delivery Scheduled",
     "allowed": "DMS Manager"},
    {"state": "Delivery Scheduled", "action": "Mark Delivered", "next_state": "Delivered",
     "allowed": "Dealer Admin"}
  ]
}
""",
    "automobile_dealership/automobile_dealership/print_format/vehicle_sale_invoice/vehicle_sale_invoice.html": """<div class="print-format" style="font-family: Arial, sans-serif;">
  <div class="header" style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px;">
    <h2>{{ frappe.db.get_single_value('Automobile Dealership Settings', 'dealership_name') }}</h2>
    <p>Authorised Dealer — {{ doc.make }}</p>
    <p>GSTIN: {{ frappe.db.get_value('Company', doc.company, 'gstin') }}</p>
  </div>

  <h3 style="text-align: center; margin-top: 15px;">VEHICLE SALE INVOICE</h3>

  <table style="width: 100%; margin-top: 10px;">
    <tr>
      <td><strong>Invoice No:</strong> {{ doc.name }}</td>
      <td style="text-align: right;"><strong>Date:</strong> {{ doc.posting_date }}</td>
    </tr>
    <tr>
      <td><strong>Customer:</strong> {{ doc.customer_name }}</td>
      <td style="text-align: right;"><strong>Mobile:</strong> {{ doc.customer_mobile }}</td>
    </tr>
  </table>

  <h4 style="margin-top: 15px;">Vehicle Details</h4>
  <table style="width: 100%; border-collapse: collapse;">
    <tr style="background: #f0f0f0;">
      <th style="border: 1px solid #ccc; padding: 6px;">VIN Number</th>
      <th style="border: 1px solid #ccc; padding: 6px;">Make / Model</th>
      <th style="border: 1px solid #ccc; padding: 6px;">Color</th>
      <th style="border: 1px solid #ccc; padding: 6px;">Year</th>
      <th style="border: 1px solid #ccc; padding: 6px;">Engine No</th>
    </tr>
    <tr>
      <td style="border: 1px solid #ccc; padding: 6px;">{{ doc.vin_number }}</td>
      <td style="border: 1px solid #ccc; padding: 6px;">{{ doc.make }} {{ doc.model }} {{ doc.variant }}</td>
      <td style="border: 1px solid #ccc; padding: 6px;">{{ doc.color }}</td>
      <td style="border: 1px solid #ccc; padding: 6px;">{{ doc.year_of_manufacture }}</td>
      <td style="border: 1px solid #ccc; padding: 6px;">{{ doc.engine_number }}</td>
    </tr>
  </table>

  <h4 style="margin-top: 15px;">Price Breakdown</h4>
  <table style="width: 100%; border-collapse: collapse;">
    <tr><td style="padding: 4px;">Ex-Showroom Price</td>
        <td style="text-align: right; padding: 4px;">₹ {{ "{:,.0f}".format(doc.ex_showroom_price or 0) }}</td></tr>
    <tr><td>Registration & RTO Charges</td>
        <td style="text-align: right;">₹ {{ "{:,.0f}".format(doc.registration_charges or 0) }}</td></tr>
    <tr><td>Insurance Premium</td>
        <td style="text-align: right;">₹ {{ "{:,.0f}".format(doc.insurance_premium or 0) }}</td></tr>
    <tr><td>Accessories</td>
        <td style="text-align: right;">₹ {{ "{:,.0f}".format(doc.accessories_total or 0) }}</td></tr>
    <tr><td>Handling Charges</td>
        <td style="text-align: right;">₹ {{ "{:,.0f}".format(doc.handling_charges or 0) }}</td></tr>
    <tr style="background: #f0f0f0; font-weight: bold;">
        <td>Total On-Road Price</td>
        <td style="text-align: right;">₹ {{ "{:,.0f}".format(doc.subtotal or 0) }}</td></tr>
    {% if doc.discount_amount %}
    <tr><td style="color: green;">Discount</td>
        <td style="text-align: right; color: green;">- ₹ {{ "{:,.0f}".format(doc.discount_amount) }}</td></tr>
    {% endif %}
    <tr style="background: #333; color: white; font-weight: bold;">
        <td style="padding: 8px;">Grand Total</td>
        <td style="text-align: right; padding: 8px;">₹ {{ "{:,.0f}".format(doc.grand_total or 0) }}</td></tr>
  </table>

  <div style="margin-top: 20px; font-size: 11px; color: #666;">
    <p>This is a computer-generated invoice. Subject to terms and conditions.</p>
  </div>
</div>
""",
    "automobile_dealership/automobile_dealership/tests/test_vehicle.py": """import frappe
import unittest
from frappe.utils import today

class TestVehicle(unittest.TestCase):

    def setUp(self):
        self.vehicle = frappe.get_doc({
            "doctype": "Vehicle",
            "vin_number": "1HGCM82633A123456",
            "make": "Maruti Suzuki",
            "model": "Swift",
            "variant": "VXI",
            "year_of_manufacture": 2024,
            "vehicle_type": "New",
            "ex_showroom_price": 800000,
            "status": "Available",
        }).insert(ignore_permissions=True)

    def test_vin_validation(self):
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Vehicle",
                "vin_number": "INVALID",
                "make": "Maruti Suzuki",
                "model": "Swift",
                "year_of_manufacture": 2024,
            }).insert()

    def test_days_in_stock_calculation(self):
        self.vehicle.oem_invoice_date = frappe.utils.add_days(today(), -30)
        self.vehicle.save()
        self.assertEqual(self.vehicle.days_in_stock, 30)

    def test_vehicle_status_on_sale(self):
        # Mark vehicle as sold
        frappe.db.set_value("Vehicle", self.vehicle.name, "status", "Sold")
        status = frappe.db.get_value("Vehicle", self.vehicle.name, "status")
        self.assertEqual(status, "Sold")

    def tearDown(self):
        frappe.delete_doc("Vehicle", self.vehicle.name, force=True)

class TestServiceJobCard(unittest.TestCase):

    def test_emi_calculation(self):
        loan = frappe.get_doc({
            "doctype": "Loan Application",
            "loan_amount": 500000,
            "interest_rate": 9.5,
            "tenure_months": 60,
        })
        loan.calculate_emi()
        self.assertAlmostEqual(loan.emi_amount, 10485, delta=50)
""",
    "automobile_dealership/setup.py": """from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\\n")

from automobile_dealership import __version__ as version

setup(
    name="automobile_dealership",
    version=version,
    description="Automobile Dealership Management",
    author="Your Company",
    author_email="dev@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
""",
    "automobile_dealership/requirements.txt": """ """,
    "automobile_dealership/automobile_dealership/__init__.py": """__version__ = '1.0.0'
""",
    "automobile_dealership/__init__.py": """"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

