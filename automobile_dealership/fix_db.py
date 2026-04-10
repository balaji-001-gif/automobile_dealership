import frappe

def run():
    print("Cleaning up database and synchronizing modules...")
    
    # 1. Clear corrupted workspaces (blank sidebar boxes)
    print("- Cleaning up blank workspaces...")
    frappe.db.sql('DELETE FROM `tabWorkspace` WHERE label IS NULL OR label = "" OR name = "automobile_dealership"')
    
    # 2. Consolidate Module Defs
    print("- Harmonizing Module Defs...")
    # Delete the redundant lowercase "automobile_dealership" if it exists
    if frappe.db.exists("Module Def", "automobile_dealership"):
        frappe.db.delete("Module Def", "automobile_dealership")
        
    # Ensure "Automobile Dealership" points to the correct app
    if frappe.db.exists("Module Def", "Automobile Dealership"):
        frappe.db.set_value("Module Def", "Automobile Dealership", "app_name", "automobile_dealership")
    
    # 3. Handle orphaned DocTypes
    # We dont need to manually delete them because bench migrate does it, 
    # but we need to ensure the Module is correct.
    
    frappe.db.commit()
    print("Cleanup successful. You can now run bench migrate.")

if __name__ == "__main__":
    run()
