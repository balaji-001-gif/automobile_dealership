import frappe

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
