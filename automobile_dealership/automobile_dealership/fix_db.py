import frappe

def run():
    print("Starting hardened database sync and cleanup...")
    
    # List of all DocTypes in the app
    doctypes = [
        "Vehicle", "Vehicle Sale", "Service Job Card", "Insurance Policy",
        "AMC Contract", "Loyalty Account", "Loyalty Point Transaction",
        "Test Drive", "Loan Application", "Vehicle Inventory Log",
        "Sales Incentive Rule", "Automobile Dealership Settings",
        "Vehicle Feature Item", "Service Job Labour Item", "Service Job Part Item"
    ]
    
    for dt in doctypes:
        if frappe.db.exists("DocType", dt):
            print(f"Aligning DocType: {dt}...")
            # Force update module and custom flag using DB set_value (safest)
            frappe.db.set_value("DocType", dt, {
                "module": "Automobile Dealership",
                "custom": 0
            })
            # Clear compiled metadata
            frappe.clear_cache(doctype=dt)
    
    # Cleanup corrupted workspaces using the ORM (schema-agnostic)
    print("Cleaning up Workspace entries via ORM...")
    workspaces = frappe.get_all("Workspace", filters={"module": "Automobile Dealership"})
    for ws in workspaces:
        print(f"Deleting workspace: {ws.name}")
        frappe.delete_doc("Workspace", ws.name, ignore_permissions=True, force=True)
    
    # Also cleanup by label just in case
    workspaces_by_label = frappe.get_all("Workspace", filters={"label": "Automobile Dealership"})
    for ws in workspaces_by_label:
        print(f"Deleting workspace by label: {ws.name}")
        frappe.delete_doc("Workspace", ws.name, ignore_permissions=True, force=True)
    
    frappe.db.commit()
    frappe.clear_cache()
    
    print("Database fixation complete. Please run bench migrate now.")

if __name__ == "__main__":
    run()
