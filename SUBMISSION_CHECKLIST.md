# OneLab Submission Checklist

Use this file as your final hand-in checklist for the OneLab reconciliation project.

## What You Have To Submit

- [ ] **1. Brainstorming thread**
  Full LLM conversation.
  Do not clean it up.

- [ ] **2. Distilled prompt**
  Use the exact prompt below:

```text
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

- [ ] **3. Claude Code / Cursor execution thread**
  Full coding thread including wrong turns and fixes.

- [ ] **4. Test cases**
  4 pytest unit tests:
  - late settlement
  - rounding gap
  - duplicate transaction
  - orphan refund

- [ ] **5. Working output**
  Include all of these:
  - deployed link
  - code zip
  - demo video
  - the 3 production caveat sentences below, verbatim

## Exact 3 Sentences To Include Verbatim

The matcher assumes `transaction_id` is a reliable join key, but real payment processors sometimes remap IDs during retries, causing false-positive "unmatched" flags. Rounding detection uses a fixed $0.01 threshold, which breaks for non-USD currencies with different decimal conventions (e.g. JPY has no sub-unit). The duplicate detector compares only the ID field, so a legitimate re-submission with a corrected amount would be silently missed and counted as a clean match.

## Project Files Already Prepared

- Codebase: [reconciler](D:/OneLab/reconciler)
- Backend app: [main.py](D:/OneLab/reconciler/backend/api/main.py)
- Engine loader: [loader.py](D:/OneLab/reconciler/backend/engine/loader.py)
- Gap detectors: [detectors.py](D:/OneLab/reconciler/backend/engine/detectors.py)
- Reconciliation matcher: [matcher.py](D:/OneLab/reconciler/backend/engine/matcher.py)
- Frontend UI: [index.html](D:/OneLab/reconciler/frontend/index.html)
- Tests: [test_detectors.py](D:/OneLab/reconciler/backend/tests/test_detectors.py)
- Transactions CSV: [transactions.csv](D:/OneLab/reconciler/backend/data/transactions.csv)
- Settlements CSV: [settlements.csv](D:/OneLab/reconciler/backend/data/settlements.csv)
- Generated report: [gaps_report.json](D:/OneLab/reconciler/backend/gaps_report.json)
- Project notes: [README.md](D:/OneLab/reconciler/README.md)
- Original spec: [IMPLEMENTATION.md](D:/OneLab/IMPLEMENTATION.md)

## What You Still Need To Prepare Manually

- [ ] Export or copy your full brainstorming LLM conversation
- [ ] Export or copy your full Claude Code / Cursor build thread
- [ ] Zip the project folder
- [ ] Deploy the app and copy the live link
- [ ] Record a short demo video

## Run Commands

Install dependencies:

```powershell
cd D:\OneLab\reconciler\backend
python -m pip install -r requirements.txt
```

Run the app:

```powershell
cd D:\OneLab\reconciler\backend
python -m uvicorn api.main:app --reload --port 8000
```

Run tests:

```powershell
cd D:\OneLab\reconciler\backend
python -m pytest tests -v
```

## Suggested Final Submission Bundle

- Brainstorming thread PDF or text export
- Distilled prompt text
- Claude Code / Cursor thread export
- Project zip from `D:\OneLab\reconciler`
- Deployed link
- Demo video
- The 3 verbatim production caveat sentences
