import frappe

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
