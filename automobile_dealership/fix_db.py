import frappe

def run():
    print("NUCLEAR CLEANUP: Deep cleaning Sidebar and Workspaces...")
    
    # 1. Identify all non-standard and corrupted workspaces
    # We delete anything that is not from Frappe, ERPNext, HRMS etc.
    # OR any record that has blank labels
    print("- Deleting corrupted and duplicate workspace records...")
    
    # Target our specific app duplicates first
    frappe.db.sql('DELETE FROM `tabWorkspace` WHERE name LIKE "%automobile_dealership%" OR label LIKE "%Automobile Dealership%"')
    
    # Target "ghost" entries (no label or no module)
    frappe.db.sql('DELETE FROM `tabWorkspace` WHERE label IS NULL OR label = "" OR module IS NULL')
    
    # Clean up the Child Table for Workspace links to be safe
    frappe.db.sql('DELETE FROM `tabWorkspace Link` WHERE parent NOT IN (SELECT name FROM `tabWorkspace`)')
    
    # 2. Consolidate Module Def
    print("- Re-registering Module Def...")
    if frappe.db.exists("Module Def", "automobile_dealership"):
        frappe.db.delete("Module Def", "automobile_dealership")
        
    if not frappe.db.exists("Module Def", "Automobile Dealership"):
        frappe.get_doc({
            "doctype": "Module Def",
            "name": "Automobile Dealership",
            "module_name": "Automobile Dealership",
            "app_name": "automobile_dealership"
        }).insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Module Def", "Automobile Dealership", "app_name", "automobile_dealership")
    
    frappe.db.commit()
    print("Cleanup complete. IMPORTANT: Run 'bench migrate' now to reload the fresh workspace from files.")

if __name__ == "__main__":
    run()
