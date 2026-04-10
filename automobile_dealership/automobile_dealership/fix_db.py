import frappe

def run():
    print("REMOVING ALL Automobile Dealership Workspaces...")
    frappe.db.sql('DELETE FROM `tabWorkspace` WHERE module = "Automobile Dealership" OR name LIKE "%automobile_dealership%" OR label LIKE "%Automobile Dealership%"')
    frappe.db.sql('DELETE FROM `tabWorkspace Link` WHERE parent NOT IN (SELECT name FROM `tabWorkspace`)')
    # Also clean up any blank ones one last time
    frappe.db.sql('DELETE FROM `tabWorkspace` WHERE label IS NULL OR label = ""')
    frappe.db.commit()
    print("Workspaces removed from database. Please run migrate and clear-cache.")

if __name__ == "__main__":
    run()
