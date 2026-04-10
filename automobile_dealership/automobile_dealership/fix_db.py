import frappe

def run():
    print("Starting database sync and cleanup...")
    
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
            print(f"Aligning {dt}...")
            # Force update module and custom flag
            frappe.db.set_value("DocType", dt, {
                "module": "Automobile Dealership",
                "custom": 0
            })
            
            # Clear compiled metadata
            frappe.clear_cache(doctype=dt)
    
    # Cleanup corrupted workspaces
    print("Cleaning up Workspace entries...")
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE module = 'Automobile Dealership' AND is_standard = 1")
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE label = 'Automobile Dealership'")
    
    frappe.db.commit()
    frappe.clear_cache()
    
    print("Database fixation complete. Please run bench migrate now.")

if __name__ == "__main__":
    run()
