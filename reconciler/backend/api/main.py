from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from engine.loader import (
    load_settlements,
    load_settlements_from_bytes,
    load_transactions,
    load_transactions_from_bytes,
)
from engine.matcher import build_report, save_report

BACKEND_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
DATA_DIR = BACKEND_DIR / "data"
REPORT_PATH = BACKEND_DIR / "gaps_report.json"
UI_PATH = FRONTEND_DIR / "index.html"

app = FastAPI(title="Payments Reconciler")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(UI_PATH)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/report")
def report() -> JSONResponse:
    txns = load_transactions(DATA_DIR / "transactions.csv")
    stls = load_settlements(DATA_DIR / "settlements.csv")
    payload = build_report(txns, stls)
    save_report(payload, REPORT_PATH)
    return JSONResponse(payload)


@app.post("/reconcile")
async def reconcile(
    transactions: UploadFile = File(...),
    settlements: UploadFile = File(...),
) -> JSONResponse:
    try:
        txns = load_transactions_from_bytes(await transactions.read())
        stls = load_settlements_from_bytes(await settlements.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = build_report(txns, stls)
    save_report(payload, REPORT_PATH)
    return JSONResponse(payload)
