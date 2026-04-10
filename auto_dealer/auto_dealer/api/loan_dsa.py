import frappe
import requests

def submit_application(loan_doc):
    settings = frappe.get_single("Auto dealer Settings")

    payload = {
        "dealer_code": settings.dealer_code,
        "customer_name": loan_doc.customer_name,
        "customer_pan": loan_doc.customer_pan,
        "customer_mobile": loan_doc.customer_mobile,
        "vehicle_type": loan_doc.vehicle_type,
        "vehicle_value": loan_doc.vehicle_value,
        "loan_amount": loan_doc.loan_amount,
        "tenure_months": loan_doc.tenure_months,
        "employment_type": loan_doc.employment_type,
        "monthly_income": loan_doc.monthly_income,
    }

    try:
        response = requests.post(
            f"{settings.dsa_api_url}/applications",
            json=payload,
            headers={"Authorization": f"Bearer {settings.dsa_api_token}"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        frappe.log_error(str(e), "Loan DSA API Error")
        return {"status": "error", "message": str(e)}
