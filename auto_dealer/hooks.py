app_name = "auto_dealer"
app_title = "Auto Dealer"
app_publisher = "Your Company"
app_description = "Automobile Dealership Management"
app_version = "1.0.0"
app_license = "MIT"

# Required apps
required_apps = ["frappe", "erpnext"]

# DocType overrides
override_doctype_class = {
    "Sales Order": "auto_dealer.overrides.sales_order.CustomSalesOrder",
    "Customer": "auto_dealer.overrides.customer.CustomCustomer",
}

# Scheduled tasks
scheduler_events = {
    "daily": [
        "auto_dealer.tasks.send_service_reminders",
        "auto_dealer.tasks.check_insurance_renewals",
        "auto_dealer.tasks.check_amc_renewals",
        "auto_dealer.tasks.oem_target_sync",
    ],
    "weekly": [
        "auto_dealer.tasks.slow_moving_inventory_alert",
    ],
    "monthly": [
        "auto_dealer.tasks.generate_oem_monthly_report",
    ],
}

# Document events
doc_events = {
    "Vehicle Sale": {
        "on_submit": [
            "auto_dealer.events.vehicle_sale.on_submit",
            "auto_dealer.events.vehicle_sale.trigger_whatsapp_confirmation",
        ],
        "on_cancel": "auto_dealer.events.vehicle_sale.on_cancel",
    },
    "Service Job Card": {
        "on_submit": "auto_dealer.events.service_job_card.on_submit",
        "on_update": "auto_dealer.events.service_job_card.update_job_status",
    },
    "Customer": {
        "after_insert": "auto_dealer.events.customer.create_crm_profile",
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
    "favicon": "/assets/auto_dealer/images/favicon.ico",
}
