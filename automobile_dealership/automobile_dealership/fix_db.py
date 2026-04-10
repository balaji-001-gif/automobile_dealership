import frappe

def run():
    print("NUCLEAR SIdebar Fix...")
    
    # 1. Delete all non-standard workspaces to force reload
    # This targets anything that isn't Standard or belongs to our app
    print("- Removing all non-system workspace records...")
    frappe.db.sql("""
        DELETE FROM `tabWorkspace` 
        WHERE is_standard = 0 
           OR label IS NULL 
           OR label = "" 
           OR module = "Automobile Dealership" 
           OR name LIKE "%automobile_dealership%"
    """)
    
    # 2. Cleanup orphaned links
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent NOT IN (SELECT name FROM `tabWorkspace`)")
    
    # 3. Ensure Module Def is correct
    print("- Resetting Module Def for Automobile Dealership...")
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
    print("Cleanup successful. Please run 'bench migrate' and 'bench clear-cache' now.")

if __name__ == "__main__":
    run()
