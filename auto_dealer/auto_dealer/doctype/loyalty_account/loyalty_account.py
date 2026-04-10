import frappe
from frappe.model.document import Document

class LoyaltyAccount(Document):

    @frappe.whitelist()
    def add_points(self, points, reference_type, reference_name, remarks=""):
        self.append("transactions", {
            "transaction_date": frappe.utils.today(),
            "points": points,
            "transaction_type": "Credit",
            "reference_doctype": reference_type,
            "reference_docname": reference_name,
            "remarks": remarks,
        })
        self.total_points = (self.total_points or 0) + points
        self.save(ignore_permissions=True)

    @frappe.whitelist()
    def redeem_points(self, points, reference_name, remarks=""):
        if points > (self.total_points or 0):
            frappe.throw("Insufficient loyalty points.")
        self.append("transactions", {
            "transaction_date": frappe.utils.today(),
            "points": -points,
            "transaction_type": "Debit",
            "reference_docname": reference_name,
            "remarks": remarks,
        })
        self.total_points = (self.total_points or 0) - points
        self.save(ignore_permissions=True)
        return points * (frappe.db.get_single_value("Auto Dealer Settings", "loyalty_point_value") or 1)
