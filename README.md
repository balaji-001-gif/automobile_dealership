# Automobile Dealership ERP (ERPNext v15+)

This repository contains the `automobile_dealership` custom Frappe app designed to provide an end-to-end dealer management system for medium-sized automobile dealerships.

## Modules Included

1. **Dealer Management System (DMS) Core**: Vehicle tracking, stock days, on-road price estimates.
2. **Vehicle Inventory Management**: Marketplace API synchronization (e.g., CarDekho).
3. **Sales & Lead Management (CRM)**: Custom Test Drive scheduling and automated lead routing.
4. **Finance, Insurance & Billing**: Loan EMI calculators, automated banking API submissions, insurance renewals.
5. **Service & After-Sales Workshop**: Service Job Cards, automated out-of-stock part requests, and technician capacity validation.
6. **HR, Payroll & Incentives**: Multi-tier sales consultant commission calculators with tie-ins to finance and insurance upsells.
7. **Marketing & Customer Retention**: Integrated WhatsApp notifications and loyalty points ledger.
8. **Analytics & OEM Reporting**: Built-in dashboards to track conversions against precise OEM volume and revenue targets.

## Setup Instructions

This app is built for **ERPNext v15+**. You must have Frappe framework installed.

```bash
# Fetch the app onto your Bench
bench get-app https://github.com/balaji-001-gif/automobile_dealership.automobile_dealership.git

# Install the app on an existing site
bench --site [your-site] install-app automobile_dealership

# Migrate existing sites (if needed)
bench --site [your-site] migrate
```

## Configuration

Once installed, use the **Automobile Dealership Settings** DocType inside ERPNext to configure your API keys for WhatsApp, CarDekho, and Loan portals.

## License

MIT License
