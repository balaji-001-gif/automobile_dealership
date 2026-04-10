app_name = "automobile_dealership"
app_title = "Automobile Dealership"
app_publisher = "Your Company"
app_description = "Automobile Dealership Management"
app_version = "1.0.0"
app_license = "MIT"

# Required apps
required_apps = ["frappe", "erpnext"]

# DocType overrides
override_doctype_class = {
    "Sales Order": "automobile_dealership.overrides.sales_order.CustomSalesOrder",
    "Customer": "automobile_dealership.overrides.customer.CustomCustomer",
}

# Scheduled tasks
scheduler_events = {
    "daily": [
        "automobile_dealership.tasks.send_service_reminders",
        "automobile_dealership.tasks.check_insurance_renewals",
        "automobile_dealership.tasks.check_amc_renewals",
        "automobile_dealership.tasks.oem_target_sync",
    ],
    "weekly": [
        "automobile_dealership.tasks.slow_moving_inventory_alert",
    ],
    "monthly": [
        "automobile_dealership.tasks.generate_oem_monthly_report",
    ],
}

# Document events
doc_events = {
    "Vehicle Sale": {
        "on_submit": [
            "automobile_dealership.events.vehicle_sale.on_submit",
            "automobile_dealership.events.vehicle_sale.trigger_whatsapp_confirmation",
        ],
        "on_cancel": "automobile_dealership.events.vehicle_sale.on_cancel",
    },
    "Service Job Card": {
        "on_submit": "automobile_dealership.events.service_job_card.on_submit",
        "on_update": "automobile_dealership.events.service_job_card.update_job_status",
    },
    "Customer": {
        "after_insert": "automobile_dealership.events.customer.create_crm_profile",
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
