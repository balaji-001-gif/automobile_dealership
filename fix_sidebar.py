import frappe

def run():
    print("Cleaning up corrupted workspaces...")
    # Delete workspaces that have no label or are empty remnants
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE label IS NULL OR label = \"\"")
    # Also delete any that might have been created with the wrong lowercase name during debugging
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = \"automobile_dealership\"")
    frappe.db.commit()
    print("Cleanup complete. Please run bench migrate now.")

if __name__ == "__main__":
    run()
