import frappe

def run():
    print("FINAL RESTORE: Correcting DocType paths for deep nesting...")
    
    # 1. Clear any old Module Def entries that might be conflicting
    frappe.db.sql("""
        DELETE FROM `tabModule Def` 
        WHERE app_name = "automobile_dealership" 
          AND name != "Automobile Dealership"
    """)
    
    # 2. Force the Module Def to point to the correct app
    if frappe.db.exists("Module Def", "Automobile Dealership"):
        frappe.db.set_value("Module Def", "Automobile Dealership", "app_name", "automobile_dealership")
        print("- Module Def 'Automobile Dealership' verified.")
    
    # 3. Nuclear clear of any "Custom" DocTypes that might be remnants
    # This forces the system to re-read them as Standard from the new paths
    frappe.db.sql("DELETE FROM `tabDocType` WHERE module = 'Automobile Dealership' AND custom = 1")
    
    frappe.db.commit()
    frappe.clear_cache()
    print("Cleanup complete. Run 'bench migrate' to restore all DocTypes.")

if __name__ == "__main__":
    run()
