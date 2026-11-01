# ReturnFlow – Data Validation Report

## 1. Overview

This report summarizes the data validation performed on the ReturnFlow dataset.

## 2. Dataset Summary

| Model | Number of Records |
|---|---:|
| Customer | 5,000 |
| Order | 30,000 |
| OrderLine | 60,000 |
| ReturnRequest | 5,000 |
| ReturnLine | 8,000 |
| ReturnAuthorization | 5,000 |
| ReturnShipment | 5,000 |
| Inspection | 8,000 |
| Refund | 5,000 |
| InventoryDisposition | 8,000 |
| ReturnEvent | 5,000 |
| **Total** | **144,000** |

## 3. Validation Checks

- Record counts and primary key uniqueness.
- Foreign key relationships.
- Returned quantities against ordered quantities.
- Refund amounts against returned product values.
- Authorization dates against request dates.
- Shipment date sequence.
- Inventory disposition and inspection relationships.

## 4. Validation Results

| Result | Count |
|---|---:|
| Total records | 144,000 |
| Errors | 0 |
| Warnings | 0 |

## 5. Conclusion

The ReturnFlow dataset successfully passed all implemented validation checks.

No errors or warnings were detected in the latest validation run.

## 6. Validation Command

```bash
python manage.py validate_data
```