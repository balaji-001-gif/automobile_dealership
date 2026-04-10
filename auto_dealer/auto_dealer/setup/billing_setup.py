import frappe

def setup_gst_accounts(company):
    gst_accounts = [
        {"account_name": "CGST Payable", "parent_account": "Duties and Taxes", "tax_rate": 14},
        {"account_name": "SGST Payable", "parent_account": "Duties and Taxes", "tax_rate": 14},
        {"account_name": "IGST Payable", "parent_account": "Duties and Taxes", "tax_rate": 28},
        {"account_name": "TCS Payable", "parent_account": "Duties and Taxes", "tax_rate": 1},
    ]

    for acc in gst_accounts:
        if not frappe.db.exists("Account", {"account_name": acc["account_name"], "company": company}):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": acc["account_name"],
                "parent_account": f"{acc['parent_account']} - {frappe.db.get_value('Company', company, 'abbr')}",
                "account_type": "Tax",
                "company": company,
            }).insert()

def create_vehicle_sale_tax_template():
    if frappe.db.exists("Sales Taxes and Charges Template", "Vehicle Sale GST 28%"):
        return

    doc = frappe.new_doc("Sales Taxes and Charges Template")
    doc.title = "Vehicle Sale GST 28%"
    doc.append("taxes", {
        "charge_type": "On Net Total",
        "account_head": "CGST Payable - AD",
        "rate": 14,
        "description": "CGST @ 14%",
    })
    doc.append("taxes", {
        "charge_type": "On Net Total",
        "account_head": "SGST Payable - AD",
        "rate": 14,
        "description": "SGST @ 14%",
    })
    doc.insert()
