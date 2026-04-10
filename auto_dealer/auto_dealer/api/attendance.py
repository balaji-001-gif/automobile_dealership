import frappe
from frappe.utils import today, now_datetime

@frappe.whitelist()
def mark_technician_attendance(employee, status="Present"):
    if frappe.db.exists("Attendance", {
        "employee": employee,
        "attendance_date": today(),
        "docstatus": ["!=", 2],
    }):
        frappe.throw(f"Attendance already marked for {employee} today.")

    att = frappe.new_doc("Attendance")
    att.employee = employee
    att.attendance_date = today()
    att.status = status
    att.company = frappe.defaults.get_user_default("Company")
    att.insert(ignore_permissions=True)
    att.submit()
    return att.name
