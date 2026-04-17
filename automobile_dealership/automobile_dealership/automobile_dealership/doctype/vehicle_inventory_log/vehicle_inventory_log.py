import frappe
from frappe.model.document import Document

class VehicleInventoryLog(Document):
    pass

@frappe.whitelist()
def get_slow_moving_vehicles(days_threshold=60):
    return frappe.db.sql('''
        SELECT
            v.name,
            v.make,
            v.model,
            v.variant,
            v.color,
            v.fuel_type,
            v.vehicle_type,
            v.ex_showroom_price,
            v.days_in_stock,
            v.location,
            v.status
        FROM `tabVehicle` v
        WHERE v.status = 'Available'
          AND v.days_in_stock > %(days)s
        ORDER BY v.days_in_stock DESC
    ''', {"days": days_threshold}, as_dict=True)
