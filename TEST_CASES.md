# OneLab Test Cases

This file documents the test cases for the payments reconciliation project.

## Scope

The project validates these reconciliation gap types:

- `late_settlement`
- `rounding_gap`
- `duplicate`
- `orphan_refund`
- `unmatched_transaction`

The official required unit tests cover the first four detector functions.

## Unit Test Cases

| Test Case ID | Test Name | Input Scenario | Expected Result |
|---|---|---|---|
| TC-01 | `test_late_settlement` | A transaction created on `2024-01-30` and settled on `2024-02-02` | 1 row returned with `gap_type = late_settlement` |
| TC-02 | `test_rounding_gap` | A transaction amount of `$100.00` and a settlement amount of `$99.99` | 1 row returned with `gap_type = rounding_gap` and `amount_diff = 0.01` |
| TC-03 | `test_duplicate_transaction` | The same `transaction_id` appears twice in `transactions.csv` with identical fields | 2 rows returned with `gap_type = duplicate` |
| TC-04 | `test_orphan_refund` | A refund row exists with no matching original transaction | 1 row returned with `gap_type = orphan_refund` |

## Test File

The implemented pytest file is:

- [test_detectors.py](D:/OneLab/reconciler/backend/tests/test_detectors.py)

## How To Run The Tests

```powershell
cd D:\OneLab\reconciler\backend
python -m pytest tests -v
```

## Expected Test Output

All four tests should pass:

```text
tests/test_detectors.py::test_late_settlement PASSED
tests/test_detectors.py::test_rounding_gap PASSED
tests/test_detectors.py::test_duplicate_transaction PASSED
tests/test_detectors.py::test_orphan_refund PASSED
```

## Manual Integration Check

You can also validate the sample CSV files through the running app.

Sample files:

- [transactions.csv](D:/OneLab/reconciler/backend/data/transactions.csv)
- [settlements.csv](D:/OneLab/reconciler/backend/data/settlements.csv)

Run the sample report:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/report | Select-Object -Expand Content
```

Expected sample result:

- `total_gaps = 6`
- `duplicate = 2`
- `late_settlement = 1`
- `orphan_refund = 1`
- `rounding_gap = 1`
- `unmatched_transaction = 1`

## Detector Mapping

| Gap Type | Source Function |
|---|---|
| `late_settlement` | `detect_late_settlements()` |
| `rounding_gap` | `detect_rounding_gaps()` |
| `duplicate` | `detect_duplicates()` |
| `orphan_refund` | `detect_orphan_refunds()` |
| `unmatched_transaction` | internal unmatched reconciliation logic |

Relevant source files:

- [detectors.py](D:/OneLab/reconciler/backend/engine/detectors.py)
- [matcher.py](D:/OneLab/reconciler/backend/engine/matcher.py)
