# ReturnFlow – Return Management System

## 1. Project Overview

ReturnFlow is a Django-based return management system designed to manage product return requests and their related activities.

The project uses synthetic e-commerce data to represent customers, orders, return requests, authorizations, shipments, inspections, refunds, inventory dispositions, and return events.

It also includes labelled edge cases to represent unusual or invalid return scenarios.

## 2. Technologies Used

- **Programming Language:** Python
- **Backend Framework:** Django
- **Database:** MySQL
- **Data Formats:** CSV, JSON, SQL
- **Development Environment:** Visual Studio Code
- **Version Control:** Git and GitHub

## 3. Project Structure

```text
Returnflow/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── returns/
│   ├── management/
│   │   └── commands/
│   │       ├── generate_data.py
│   │       ├── generate_edge_cases.py
│   │       └── export_data.py
│   ├── migrations/
│   ├── models.py
│   ├── admin.py
│   └── ...
│
├── exports/
│   ├── CSV files
│   ├── JSON files
│   ├── ground_truth.csv
│   ├── ground_truth.json
│   └── seed_data.sql
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── SOURCE_MANIFEST.md
```

## 4. Database Entities

The project contains the following entities:

1. Customer
2. Order
3. OrderLine
4. ReturnRequest
5. ReturnLine
6. ReturnAuthorization
7. ReturnShipment
8. Inspection
9. Refund
10. InventoryDisposition
11. ReturnEvent
12. GroundTruth

## 5. Dataset Details

The baseline synthetic dataset contains:

| Entity | Records |
|---|---:|
| Customers | 5,000 |
| Orders | 30,000 |
| Order Lines | 60,000 |
| Return Requests | 5,000 |
| Return Lines | 8,000 |
| Return Authorizations | 5,000 |
| Return Shipments | 5,000 |
| Inspections | 8,000 |
| Refunds | 5,000 |
| Inventory Dispositions | 8,000 |
| Return Events | 5,000 |

GroundTruth contains five labelled edge-case records.

## 6. Return Management Data

The database represents the main stages of a return process:

- Customer places an order.
- Order contains one or more order lines.
- Customer requests a return.
- Return lines identify the products and quantities being returned.
- Authorization records represent return approval information.
- Shipment records track return movement.
- Inspection records capture returned product conditions.
- Refund records represent refund transactions or attempts.
- Inventory disposition records capture inventory decisions.
- Return events maintain a history of return-related activities.

## 7. Edge Cases and Ground Truth

Five labelled edge cases are included:

| Edge Case | Expected Decision |
|---|---|
| Excess return quantity | REJECT_EXCESS_QUANTITY |
| Excess refund | BLOCK_REFUND |
| Restock before inspection | BLOCK_RESTOCK |
| Late return | REJECT_WITHOUT_OVERRIDE |
| Duplicate refund | BLOCK_DUPLICATE_PAYOUT |

GroundTruth stores the expected decision separately from the normal dataset.

The late-return scenario uses an assumed 30-day return window.

These records are intended to support validation and future business-rule testing. The labels do not by themselves mean that a complete automated rule engine has been implemented.

## 8. Data Generation

The synthetic dataset is generated using a Django management command.

```bash
python manage.py generate_data
```

The generator uses a fixed random seed:

```text
20261022
```

The fixed seed is intended to support repeatable data generation.

The edge cases can be generated using:

```bash
python manage.py generate_edge_cases
```

**Note:** The current database already contains generated data and labelled edge cases. Do not run destructive regeneration commands against it without taking a backup.

## 9. Data Export

The project supports CSV and JSON exports.

Run:

```bash
python manage.py export_data
```

The export directory contains the normal entity exports and separate GroundTruth exports.

A MySQL SQL dump is also included:

```text
exports/seed_data.sql
```

## 10. Installation and Setup

### Prerequisites

- Python
- Django
- MySQL Server
- Git

### Clone the repository

```bash
git clone https://github.com/SrinidhiBejjenki/YottaFlex-Return-Management.git
```

### Move into the project directory

```bash
cd YottaFlex-Return-Management
```

### Create a virtual environment

```bash
python -m venv myenv
```

### Activate the virtual environment (Windows PowerShell)

```powershell
.\myenv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file using the provided `.env.example` file and configure your local database credentials.

Do not commit your actual `.env` file or database password.

### Run migrations

```bash
python manage.py migrate
```

### Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## 11. Important Notes

- All generated customer and transaction records are synthetic.
- No real customer or payment information is used.
- GroundTruth records are exported separately from the normal input datasets.
- The SQL dump represents the database at export time.
- The project is a development and challenge implementation, not a production payment system.

s