import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 150},
        {"label": "Variant", "fieldname": "variant", "fieldtype": "Data", "width": 120},
        {"label": "Color", "fieldname": "color", "fieldtype": "Data", "width": 100},
        {"label": "Fuel Type", "fieldname": "fuel_type", "fieldtype": "Data", "width": 100},
        {"label": "Units Sold", "fieldname": "units_sold", "fieldtype": "Int", "width": 100},
        {"label": "Retail Revenue", "fieldname": "retail_revenue", "fieldtype": "Currency", "width": 150},
        {"label": "Finance Penetration %", "fieldname": "finance_pct", "fieldtype": "Percent", "width": 150},
        {"label": "Insurance Penetration %", "fieldname": "insurance_pct", "fieldtype": "Percent", "width": 160},
        {"label": "Avg Discount", "fieldname": "avg_discount", "fieldtype": "Currency", "width": 130},
    ]

def get_data(filters):
    conditions = []
    if filters.get("month"):
        conditions.append(f"MONTH(vs.posting_date) = {filters['month']}")
    if filters.get("year"):
        conditions.append(f"YEAR(vs.posting_date) = {filters['year']}")

    where_clause = "AND " + " AND ".join(conditions) if conditions else ""

    return frappe.db.sql(f'''
        SELECT
            vs.model,
            vs.variant,
            vs.color,
            vs.fuel_type,
            COUNT(*) as units_sold,
            SUM(vs.grand_total) as retail_revenue,
            ROUND(SUM(vs.finance_done) / COUNT(*) * 100, 1) as finance_pct,
            ROUND(SUM(vs.insurance_done) / COUNT(*) * 100, 1) as insurance_pct,
            ROUND(AVG(vs.discount_amount), 0) as avg_discount
        FROM `tabVehicle Sale` vs
        WHERE vs.docstatus = 1
        {where_clause}
        GROUP BY vs.model, vs.variant, vs.color, vs.fuel_type
        ORDER BY units_sold DESC
    ''', as_dict=True)
