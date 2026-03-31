# Onelab — AI Fitness Assessment: Implementation Guide

**Time:** 2 hours | **Tools:** Any AI IDE (Claude Code / Cursor) | **Stack:** Python + FastAPI + HTML

---

## Problem Statement

A payments company's books don't balance at month end. The platform records a **transaction** instantly when a customer pays. The bank **batches and settles** funds 1–2 days later. At month end, every transaction should have a matching settlement. Find out why they don't match.

---

## Assumptions

> State these in your submission — there are no wrong ones as long as you name them.

- All amounts are in USD with 2 decimal places
- `transaction_id` is the primary join key between datasets
- Settlement batches may cover multiple transactions
- "Month end" means calendar month boundary (e.g. Jan 31 → Feb 1)
- Rounding differences are ≤ $0.02 per transaction
- Refunds are negative-amount transactions with `type = "refund"`
- A duplicate means identical `transaction_id` appearing more than once in the same file

---

## Project Structure

```
reconciler/
├── data/
│   ├── transactions.csv
│   └── settlements.csv
├── engine/
│   ├── loader.py          # CSV ingestion + schema validation
│   ├── matcher.py         # Join logic: transactions ↔ settlements
│   └── detectors.py       # One function per gap type
├── api/
│   └── main.py            # FastAPI: POST /reconcile, GET /report
├── ui/
│   └── index.html         # Drag-drop upload + results table
├── tests/
│   └── test_detectors.py  # 4 unit tests (one per gap type)
├── requirements.txt
└── README.md
```

---

## Step 1 — Generate Test Data

No files are provided. Use this prompt in your AI IDE to generate them:

```
Generate two CSV files for a payments reconciliation exercise.

transactions.csv columns:
  transaction_id, customer_id, amount, currency, created_at, status, type

settlements.csv columns:
  settlement_id, transaction_id, settled_amount, settled_at, bank_reference

Generate 50 clean matching rows, then plant exactly these 4 anomalies:
  1. One transaction from 2024-01-30 that settles on 2024-02-02 (next month)
  2. One transaction where settled_amount differs by $0.01 (rounding gap)
  3. One duplicate transaction_id in transactions.csv with identical fields
  4. One refund (negative amount, type="refund") with no matching original transaction_id

Output valid CSV only. No explanation.
```

---

## Step 2 — Core Engine

### `loader.py`
```python
import pandas as pd

def load_transactions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["created_at"])
    assert {"transaction_id","amount","created_at","type"}.issubset(df.columns)
    return df

def load_settlements(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["settled_at"])
    assert {"settlement_id","transaction_id","settled_amount","settled_at"}.issubset(df.columns)
    return df
```

### `detectors.py` — Four gap detectors

```python
import pandas as pd

def detect_late_settlements(txns, stls):
    """Settlement month != transaction month."""
    merged = txns.merge(stls, on="transaction_id", how="inner")
    mask = merged["settled_at"].dt.month != merged["created_at"].dt.month
    return merged[mask][["transaction_id","created_at","settled_at","amount"]] \
           .assign(gap_type="late_settlement")

def detect_rounding_gaps(txns, stls, threshold=0.005):
    """Settled amount differs from transaction amount."""
    merged = txns.merge(stls, on="transaction_id", how="inner")
    merged["diff"] = (merged["settled_amount"] - merged["amount"]).abs()
    mask = merged["diff"] > threshold
    return merged[mask][["transaction_id","amount","settled_amount","diff"]] \
           .assign(gap_type="rounding_gap")

def detect_duplicates(txns):
    """Duplicate transaction_id in transactions."""
    dupes = txns[txns.duplicated("transaction_id", keep=False)]
    return dupes[["transaction_id","amount","created_at"]] \
           .assign(gap_type="duplicate")

def detect_orphan_refunds(txns):
    """Refund with no matching original transaction."""
    refunds = txns[txns["type"] == "refund"].copy()
    originals = set(txns[txns["type"] != "refund"]["transaction_id"])
    # Refund references original via a ref_transaction_id column, or by convention
    orphans = refunds[~refunds["transaction_id"].isin(originals)]
    return orphans[["transaction_id","amount","created_at"]] \
           .assign(gap_type="orphan_refund")
```

### `matcher.py`
```python
import pandas as pd

def run_reconciliation(txns, stls):
    from engine.detectors import (detect_late_settlements, detect_rounding_gaps,
                                   detect_duplicates, detect_orphan_refunds)
    gaps = pd.concat([
        detect_late_settlements(txns, stls),
        detect_rounding_gaps(txns, stls),
        detect_duplicates(txns),
        detect_orphan_refunds(txns),
    ], ignore_index=True)

    unmatched = txns[~txns["transaction_id"].isin(stls["transaction_id"])]
    unmatched = unmatched.assign(gap_type="unmatched_transaction")

    all_gaps = pd.concat([gaps, unmatched], ignore_index=True)
    return all_gaps
```

---

## Step 3 — API Layer

### `api/main.py`
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd, io
from engine.loader import load_transactions, load_settlements
from engine.matcher import run_reconciliation

app = FastAPI(title="Payments Reconciler")

@app.post("/reconcile")
async def reconcile(
    transactions: UploadFile = File(...),
    settlements: UploadFile = File(...)
):
    txns = pd.read_csv(io.BytesIO(await transactions.read()), parse_dates=["created_at"])
    stls = pd.read_csv(io.BytesIO(await settlements.read()), parse_dates=["settled_at"])
    gaps = run_reconciliation(txns, stls)

    summary = gaps.groupby("gap_type").agg(
        count=("transaction_id","count"),
        total_exposure=("amount", lambda x: x.abs().sum())
    ).reset_index().to_dict(orient="records")

    return JSONResponse({
        "gaps": gaps.to_dict(orient="records"),
        "summary": summary,
        "total_gaps": len(gaps)
    })
```

Run with: `uvicorn api.main:app --reload`

---

## Step 4 — Test Cases

### `tests/test_detectors.py`

| Test | Input | Expected Output |
|------|-------|-----------------|
| `test_late_settlement` | txn Jan 30, settled Feb 2 | 1 row, `gap_type = late_settlement` |
| `test_rounding_gap` | txn $100.00, settled $99.99 | 1 row, `diff = 0.01` |
| `test_duplicate_transaction` | same `transaction_id` twice | 2 rows flagged as duplicate |
| `test_orphan_refund` | refund with unknown `transaction_id` | 1 row, `gap_type = orphan_refund` |

**Distilled prompt for Claude Code:**
```
Write pytest unit tests for detectors.py.
Use inline pd.DataFrame fixtures (no CSV files).
One test per gap type: late settlement, rounding gap, duplicate, orphan refund.
Each test should assert gap_type value and row count.
```

---

## Step 5 — Distilled Prompt for AI Coding Tool

Feed this single prompt into Claude Code or Cursor:

```
Build a Python payments reconciliation tool.

Inputs: transactions.csv (transaction_id, customer_id, amount, currency,
        created_at, status, type) and settlements.csv (settlement_id,
        transaction_id, settled_amount, settled_at, bank_reference).

Detect these gaps:
  - settlement month != transaction month (late settlement)
  - abs(settled_amount - amount) > 0.005 (rounding gap)
  - duplicate transaction_id in transactions (duplicate)
  - refund with type=="refund" where original transaction_id not found (orphan refund)
  - transactions with no matching settlement (unmatched)

Output: gaps_report.json with {gap_type, transaction_id, details, amount_diff}
        and a summary with count + total $ exposure per gap type.

Also build a FastAPI endpoint POST /reconcile that accepts both CSVs and returns
the gaps as JSON. Add 4 pytest unit tests using inline DataFrame fixtures.
```

---

## Step 6 — What It Gets Wrong in Production

> Include these 3 sentences verbatim in your submission:

The matcher assumes `transaction_id` is a reliable join key, but real payment processors sometimes remap IDs during retries, causing false-positive "unmatched" flags. Rounding detection uses a fixed $0.01 threshold, which breaks for non-USD currencies with different decimal conventions (e.g. JPY has no sub-unit). The duplicate detector compares only the ID field, so a legitimate re-submission with a corrected amount would be silently missed and counted as a clean match.

---

## Submission Checklist

- [ ] **1 Brainstorming thread** — Full LLM convo, do not clean it up
- [ ] **2 Distilled prompt** — The single prompt from Step 5 above
- [ ] **3 Claude Code thread** — Full execution including wrong turns
- [ ] **4 Test cases** — 4 pytest tests from Step 4
- [ ] **5 Working output** — Deployed link + code zip + demo video + 3 sentences (Step 6)

---

## Requirements

```
fastapi
uvicorn
pandas
pytest
python-multipart
```

Install: `pip install -r requirements.txt`
Run: `uvicorn api.main:app --reload --port 8000`
Test: `pytest tests/ -v`
```
