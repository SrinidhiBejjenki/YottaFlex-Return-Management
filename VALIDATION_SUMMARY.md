# ReturnFlow – Validation Summary

## 1. Validation Overview

The ReturnFlow dataset was checked using a custom Django management command:

```bash
python manage.py validate_data
```

## 2. Dataset Record Counts

| Entity | Records |
|---|---:|
| Customer | 5,000 |
| Order | 30,000 |
| OrderLine | 60,000 |
| ReturnRequest | 5,000 |
| ReturnLine | 8,000 |
| ReturnAuthorization | 5,000 |
| ReturnShipment | 5,000 |
| Inspection | 8,000 |
| Refund | 5,002 |
| InventoryDisposition | 8,001 |
| ReturnEvent | 5,000 |

## 3. Validation Checks

The validation command checks:

- Primary-key uniqueness
- Foreign-key relationships
- Return quantity consistency
- Refund amount consistency
- Authorization date ordering
- Shipment date ordering
- Inspection and inventory disposition relationships
- Labelled edge cases

## 4. Validation Results

| Result | Count |
|---|---:|
| Unexpected errors | 0 |
| Warnings | 0 |
| Expected anomalies detected | 4 |

**Final status:** Validation completed with no unexpected errors.

## 5. Expected Edge Cases

The project contains five labelled GroundTruth scenarios:

1. Excess return quantity
2. Excess refund
3. Restock before inspection
4. Late return without override
5. Duplicate refund attempt

Four anomaly types were detected by the current validation command. The late-return label is present but does not yet have a dedicated validation check.

## 6. Conclusion

The current validation run completed successfully with zero unexpected errors and zero warnings. The deliberately generated anomalies were retained and identified separately using GroundTruth labels.