# ReturnFlow - Source Manifest

## 1. Data Source

All data used in this project is synthetically generated.
No real customer or payment information is used.

## 2. Data Generation

- Framework: Django
- Database: MySQL
- Programming Language: Python
- Generator: generate_data.py
- Random Seed: 20261022

## 3. Data Entities

- Customer
- Order
- OrderLine
- ReturnRequest
- ReturnLine
- ReturnAuthorization
- ReturnShipment
- Inspection
- Refund
- InventoryDisposition
- ReturnEvent
- GroundTruth

## 4. Baseline Dataset

- Customers: 5,000
- Orders: 30,000
- Order Lines: 60,000
- Return Requests: 5,000
- Return Lines: 8,000

## 5. Edge Cases

Five labelled scenarios are generated:

1. Excess return quantity
2. Excess refund
3. Restock before inspection
4. Late return without override
5. Duplicate refund attempt

Expected decisions are stored separately
in GroundTruth records.

## 6. Reproducibility

The generator uses a fixed random seed:
20261022

The same seed is intended to produce
repeatable synthetic data.

## 7. External Data

No external datasets or third-party
customer records were used.

## 8. Export Formats

- CSV
- JSON
- SQL

GroundTruth is exported separately from
the normal input datasets.