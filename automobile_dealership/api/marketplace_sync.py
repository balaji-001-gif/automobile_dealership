import frappe
import requests

def sync_to_cardekho(vehicle_name):
    # Sync vehicle listing to CarDekho partner portal
    vehicle = frappe.get_doc("Vehicle", vehicle_name)
    settings = frappe.get_single("Automobile Dealership Settings")

    payload = {
        "dealer_id": settings.cardekho_dealer_id,
        "vin": vehicle.vin_number,
        "make": vehicle.make,
        "model": vehicle.model,
        "variant": vehicle.variant,
        "year": vehicle.year_of_manufacture,
        "color": vehicle.color,
        "fuel": vehicle.fuel_type,
        "transmission": vehicle.transmission,
        "price": vehicle.ex_showroom_price,
        "odometer": vehicle.odometer_reading,
        "images": [vehicle.image] if vehicle.image else [],
    }

    try:
        response = requests.post(
            settings.cardekho_api_url,
            json=payload,
            headers={"Authorization": f"Bearer {settings.cardekho_api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        frappe.logger().info(f"Vehicle {vehicle_name} synced to CarDekho")
        return {"status": "success", "listing_id": response.json().get("listing_id")}
    except Exception as e:
        frappe.log_error(str(e), "CarDekho Sync Error")
        return {"status": "error", "message": str(e)}
