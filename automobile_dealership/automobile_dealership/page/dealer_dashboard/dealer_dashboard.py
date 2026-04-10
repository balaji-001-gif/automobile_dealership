import frappe

@frappe.whitelist()
def get_dashboard_data():
    from frappe.utils import today, get_first_day, get_last_day, add_months

    today_date = today()
    month_start = get_first_day(today_date)
    month_end = get_last_day(today_date)
    prev_month_start = get_first_day(add_months(today_date, -1))
    prev_month_end = get_last_day(add_months(today_date, -1))

    return {
        "vehicles": {
            "available": frappe.db.count("Vehicle", {"status": "Available"}),
            "booked": frappe.db.count("Vehicle", {"status": "Booked"}),
            "sold_this_month": frappe.db.count("Vehicle Sale", {
                "docstatus": 1,
                "posting_date": ["between", [month_start, month_end]],
            }),
            "slow_moving": frappe.db.count("Vehicle", {
                "status": "Available",
                "days_in_stock": [">", 60],
            }),
        },
        "revenue": {
            "vehicle_sales_mtd": get_vehicle_sales_revenue(month_start, month_end),
            "service_revenue_mtd": get_service_revenue(month_start, month_end),
            "parts_revenue_mtd": get_parts_revenue(month_start, month_end),
        },
        "leads": {
            "new_today": frappe.db.count("Lead", {"creation": [">=", today_date]}),
            "open": frappe.db.count("Lead", {"status": "Open"}),
            "converted_mtd": frappe.db.count("Lead", {
                "status": "Converted",
                "modified": ["between", [month_start, month_end]],
            }),
        },
        "service": {
            "open_jobs": frappe.db.count("Service Job Card", {
                "status": ["in", ["Open", "Work in Progress"]],
            }),
            "completed_today": frappe.db.count("Service Job Card", {
                "status": "Completed",
                "modified": [">=", today_date],
            }),
            "pending_delivery": frappe.db.count("Service Job Card", {
                "status": "Completed",
                "is_delivered": 0,
            }),
        },
        "oem_targets": get_oem_target_progress(month_start, month_end),
    }

def get_vehicle_sales_revenue(start, end):
    result = frappe.db.sql('''
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabVehicle Sale`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(start)s AND %(end)s
    ''', {"start": start, "end": end})
    return result[0][0] if result else 0

def get_service_revenue(start, end):
    result = frappe.db.sql('''
        SELECT COALESCE(SUM(final_total), 0) as total
        FROM `tabService Job Card`
        WHERE docstatus = 1
          AND posting_date BETWEEN %(start)s AND %(end)s
    ''', {"start": start, "end": end})
    return result[0][0] if result else 0

def get_parts_revenue(start, end):
    return frappe.db.sql('''
        SELECT COALESCE(SUM(si.base_grand_total), 0)
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.is_parts_invoice = 1
          AND si.posting_date BETWEEN %(start)s AND %(end)s
    ''', {"start": start, "end": end})[0][0] or 0

def get_oem_target_progress(month_start, month_end):
    target = frappe.db.get_value("OEM Target", {
        "month": frappe.utils.getdate(month_start).month,
        "year": frappe.utils.getdate(month_start).year,
    }, ["target_volume", "target_revenue"])

    if not target:
        return {"target": 0, "achieved": 0, "percent": 0}

    achieved = frappe.db.count("Vehicle Sale", {
        "docstatus": 1,
        "posting_date": ["between", [month_start, month_end]],
    })

    return {
        "target": target[0] or 0,
        "achieved": achieved,
        "percent": round((achieved / target[0]) * 100, 1) if target[0] else 0,
    }
