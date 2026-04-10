import frappe
import unittest
from frappe.utils import today

class TestVehicle(unittest.TestCase):

    def setUp(self):
        self.vehicle = frappe.get_doc({
            "doctype": "Vehicle",
            "vin_number": "1HGCM82633A123456",
            "make": "Maruti Suzuki",
            "model": "Swift",
            "variant": "VXI",
            "year_of_manufacture": 2024,
            "vehicle_type": "New",
            "ex_showroom_price": 800000,
            "status": "Available",
        }).insert(ignore_permissions=True)

    def test_vin_validation(self):
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc({
                "doctype": "Vehicle",
                "vin_number": "INVALID",
                "make": "Maruti Suzuki",
                "model": "Swift",
                "year_of_manufacture": 2024,
            }).insert()

    def test_days_in_stock_calculation(self):
        self.vehicle.oem_invoice_date = frappe.utils.add_days(today(), -30)
        self.vehicle.save()
        self.assertEqual(self.vehicle.days_in_stock, 30)

    def test_vehicle_status_on_sale(self):
        # Mark vehicle as sold
        frappe.db.set_value("Vehicle", self.vehicle.name, "status", "Sold")
        status = frappe.db.get_value("Vehicle", self.vehicle.name, "status")
        self.assertEqual(status, "Sold")

    def tearDown(self):
        frappe.delete_doc("Vehicle", self.vehicle.name, force=True)

class TestServiceJobCard(unittest.TestCase):

    def test_emi_calculation(self):
        loan = frappe.get_doc({
            "doctype": "Loan Application",
            "loan_amount": 500000,
            "interest_rate": 9.5,
            "tenure_months": 60,
        })
        loan.calculate_emi()
        self.assertAlmostEqual(loan.emi_amount, 10485, delta=50)
