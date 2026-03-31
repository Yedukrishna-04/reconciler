# Reconciler - AI IDE Check Instructions

Use this file when you want an AI IDE like Claude Code or Cursor to review the current project and verify that everything still works after the folder split.

## Current Project Structure

The project has already been reorganized into separate backend and frontend folders:

```text
reconciler/
├── backend/
│   ├── api/
│   │   └── main.py
│   ├── data/
│   │   ├── transactions.csv
│   │   └── settlements.csv
│   ├── engine/
│   │   ├── loader.py
│   │   ├── detectors.py
│   │   └── matcher.py
│   ├── tests/
│   │   └── test_detectors.py
│   ├── gaps_report.json
│   └── requirements.txt
└── frontend/
    └── index.html
```

Important:

- The backend code lives in `backend/`
- The frontend HTML lives in `frontend/`
- FastAPI still serves the frontend page at `/`
- Do not move files back to the old `api/`, `engine/`, `data/`, `tests/`, or `ui/` root-level layout

## What The AI IDE Should Check

Ask the AI IDE to verify all of these:

1. The separated folder structure is correct
2. Backend imports still work from `backend/`
3. `backend/api/main.py` correctly serves `frontend/index.html`
4. CSV files are present in `backend/data/`
5. Pytest tests pass from the `backend/` directory
6. FastAPI routes `/`, `/health`, `/report`, and `/reconcile` still work
7. Deployment docs and Claude deployment instructions match the new layout

## Best Prompt To Paste Into Claude / Cursor

Paste this prompt exactly:

```text
Please verify my current payments reconciler project after a folder split.

Project root:
D:\OneLab\reconciler

Current structure:
- backend/api/main.py
- backend/engine/loader.py
- backend/engine/detectors.py
- backend/engine/matcher.py
- backend/data/transactions.csv
- backend/data/settlements.csv
- backend/tests/test_detectors.py
- backend/requirements.txt
- frontend/index.html

Important:
- backend and frontend are now in separate folders
- FastAPI still serves the frontend HTML from GET /
- this is the intended architecture
- do not move files back to the old structure

Please check all of the following:
1. imports and file paths are correct
2. backend/api/main.py correctly references the frontend folder
3. sample CSV files exist
4. pytest tests pass
5. GET / returns the frontend
6. GET /health returns status JSON
7. GET /report returns sample reconciliation JSON
8. deployment docs match the new structure

Run the necessary checks, describe any problems you find, and propose fixes only if something is broken.
```

## Prompt To Ask The AI IDE To Run Local Verification

Use this when you want the AI IDE to actually execute checks:

```text
Run a full verification of this project from the backend folder.

Use:
1. cd D:\OneLab\reconciler\backend
2. python -m pip install -r requirements.txt
3. python -m pytest tests -v
4. run the FastAPI app
5. verify:
   - GET /
   - GET /health
   - GET /report

Expected:
- all 4 pytest tests pass
- / returns the frontend HTML
- /health returns {"status":"ok"}
- /report returns JSON with total_gaps = 6
```

## Prompt To Ask The AI IDE To Inspect The Backend/Frontend Pathing

Use this if you specifically want the AI IDE to inspect the moved file paths:

```text
Check whether backend/api/main.py correctly serves the frontend from the sibling frontend folder.

Current expectation:
- backend/api/main.py should use the backend folder for data and report paths
- it should use the sibling frontend/index.html for the UI path
- backend/data should be used for transactions.csv and settlements.csv
- backend/gaps_report.json should be used for the generated report

Confirm that this is implemented correctly and point out any path issues.
```

## Prompt To Ask The AI IDE To Review Deployment Docs

Use this prompt to make Claude/Cursor review the deployment notes:

```text
Review these docs and confirm they match the current backend/frontend split:
- D:\OneLab\CLAUDE_DEPLOYMENT_INSTRUCTIONS.md
- D:\OneLab\DEPLOYMENT.md
- D:\OneLab\SUBMISSION_CHECKLIST.md
- D:\OneLab\TEST_CASES.md
- D:\OneLab\reconciler\README.md

Important:
- backend is in reconciler/backend
- frontend is in reconciler/frontend
- backend/requirements.txt is the dependency file
- deployment should account for both backend and frontend folders

Tell me if any file still points to the old structure.
```

## Expected Healthy State

If everything is correct, the AI IDE should confirm:

- `python -m pytest tests -v` passes all 4 tests from `reconciler/backend`
- `GET /` returns the frontend page
- `GET /health` returns:

```json
{"status":"ok"}
```

- `GET /report` returns JSON and includes:

```text
total_gaps = 6
```

- the sample report includes these gap types:
  - `duplicate`
  - `late_settlement`
  - `orphan_refund`
  - `rounding_gap`
  - `unmatched_transaction`

## What The AI IDE Should Not Change

Unless something is broken, the AI IDE should not:

- move frontend back under backend
- move backend files back to the old root-level structure
- add a separate frontend framework
- rewrite the project into React/Vue
- change the detector rules
- regenerate the CSV files unnecessarily

## Quick Manual Check Commands

You can also run these yourself:

```powershell
cd D:\OneLab\reconciler\backend
python -m pytest tests -v
python -m uvicorn api.main:app --reload --port 8000
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/report`

## Summary

This file is now for **checking the current separated backend/frontend project**, not for applying the old pre-split fixes.

If you give this to Claude or Cursor, tell it to **verify the current architecture, not revert it**.
