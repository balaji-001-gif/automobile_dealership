import frappe

def run():
    print("RESTORE MODE: Synchronizing DocType metadata...")
    
    # 1. Clean up stale Module Defs
    # We want "Automobile Dealership" to be the ONLY standard module for this app
    module_name = "Automobile Dealership"
    app_name = "automobile_dealership"
    
    # Delete conflicting lowercase or misspelled module defs
    frappe.db.sql("DELETE FROM `tabModule Def` WHERE name != %s AND (name LIKE '%%automobile%%' OR app_name = %s)", (module_name, app_name))
    
    # Forcefully update/create the correct Module Def
    if frappe.db.exists("Module Def", module_name):
        frappe.db.set_value("Module Def", module_name, "app_name", app_name)
        print(f"- Updated {module_name} to point to {app_name}")
    else:
        frappe.get_doc({
            "doctype": "Module Def",
            "name": module_name,
            "module_name": module_name,
            "app_name": app_name
        }).insert(ignore_permissions=True)
        print(f"- Created standard Module Def: {module_name}")
    
    # 2. Clear corrupted DocType paths from the server-side cache
    # This forces Frappe to re-calculate where folders are during the next migrate
    print("- Clearing metadata cache...")
    frappe.clear_cache()
    
    frappe.db.commit()
    print("Database metadata restored. Please run 'bench migrate' to re-import all DocTypes.")

if __name__ == "__main__":
    run()
