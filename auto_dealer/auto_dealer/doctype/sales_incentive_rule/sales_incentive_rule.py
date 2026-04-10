import frappe
from frappe.model.document import Document

class SalesIncentiveRule(Document):
    pass

@frappe.whitelist()
def calculate_consultant_incentive(employee, month, year):
    sales = frappe.db.sql('''
        SELECT
            vs.name,
            vs.vehicle,
            vs.grand_total,
            vs.make,
            vs.model,
            vs.vehicle_type,
            vs.finance_done,
            vs.insurance_done,
            vs.accessories_total
        FROM `tabVehicle Sale` vs
        WHERE vs.sales_consultant = %(employee)s
          AND MONTH(vs.posting_date) = %(month)s
          AND YEAR(vs.posting_date) = %(year)s
          AND vs.docstatus = 1
    ''', {"employee": employee, "month": month, "year": year}, as_dict=True)

    rules = frappe.get_all(
        "Sales Incentive Rule",
        filters={"is_active": 1},
        fields=["*"],
        order_by="min_sales_count asc",
    )

    total_incentive = 0
    breakdown = []

    for sale in sales:
        vehicle_incentive = get_vehicle_incentive(sale, rules)
        total_incentive += vehicle_incentive

        if sale.finance_done:
            finance_bonus = frappe.db.get_single_value(
                "Auto Dealer Settings", "finance_crosssell_bonus"
            ) or 500
            total_incentive += finance_bonus

        if sale.insurance_done:
            insurance_bonus = frappe.db.get_single_value(
                "Auto Dealer Settings", "insurance_crosssell_bonus"
            ) or 300
            total_incentive += insurance_bonus

        if sale.accessories_total:
            accessories_commission = sale.accessories_total * 0.05
            total_incentive += accessories_commission

        breakdown.append({
            "sale": sale.name,
            "vehicle": sale.vehicle,
            "vehicle_incentive": vehicle_incentive,
            "finance_bonus": finance_bonus if sale.finance_done else 0,
            "insurance_bonus": insurance_bonus if sale.insurance_done else 0,
            "accessories_commission": accessories_commission if sale.accessories_total else 0,
        })

    return {
        "employee": employee,
        "month": month,
        "year": year,
        "total_sales": len(sales),
        "total_incentive": round(total_incentive, 2),
        "breakdown": breakdown,
    }

def get_vehicle_incentive(sale, rules):
    for rule in rules:
        if sale.vehicle_type == rule.vehicle_type:
            return rule.incentive_amount
    return 0
