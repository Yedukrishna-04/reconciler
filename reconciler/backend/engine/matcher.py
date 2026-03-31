from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from engine.detectors import (
    REPORT_COLUMNS,
    detect_duplicates,
    detect_late_settlements,
    detect_orphan_refunds,
    detect_rounding_gaps,
)


def _detect_unmatched_transactions(txns: pd.DataFrame, stls: pd.DataFrame) -> pd.DataFrame:
    unmatched = txns.loc[~txns["transaction_id"].isin(stls["transaction_id"])].copy()
    if unmatched.empty:
        return pd.DataFrame(columns=REPORT_COLUMNS)

    unmatched["settled_amount"] = pd.NA
    unmatched["settled_at"] = pd.NaT
    unmatched["amount_diff"] = 0.0
    unmatched["details"] = unmatched["transaction_id"].map(
        lambda transaction_id: f"Transaction {transaction_id} has no matching settlement row."
    )
    unmatched["gap_type"] = "unmatched_transaction"
    return unmatched[REPORT_COLUMNS]


def run_reconciliation(txns: pd.DataFrame, stls: pd.DataFrame) -> pd.DataFrame:
    frames = [
        detect_late_settlements(txns, stls),
        detect_rounding_gaps(txns, stls),
        detect_duplicates(txns),
        detect_orphan_refunds(txns),
        _detect_unmatched_transactions(txns, stls),
    ]
    gaps = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)
    if gaps.empty:
        return pd.DataFrame(columns=REPORT_COLUMNS + ["exposure_amount"])

    gaps["amount"] = pd.to_numeric(gaps["amount"], errors="coerce").round(2)
    gaps["settled_amount"] = pd.to_numeric(gaps["settled_amount"], errors="coerce").round(2)
    gaps["amount_diff"] = pd.to_numeric(gaps["amount_diff"], errors="coerce").fillna(0.0).round(2)

    gaps["exposure_amount"] = gaps["amount"].abs()
    rounding_mask = gaps["gap_type"] == "rounding_gap"
    gaps.loc[rounding_mask, "exposure_amount"] = gaps.loc[rounding_mask, "amount_diff"]
    gaps["exposure_amount"] = pd.to_numeric(gaps["exposure_amount"], errors="coerce").fillna(0.0).round(2)

    return gaps


def _frame_to_records(frame: pd.DataFrame) -> list[dict]:
    if frame.empty:
        return []

    output = frame.copy()
    for column in ["created_at", "settled_at"]:
        if column in output.columns:
            output[column] = output[column].dt.strftime("%Y-%m-%d")
            output[column] = output[column].where(output[column].notna(), None)

    for column in ["amount", "settled_amount", "amount_diff", "exposure_amount"]:
        if column in output.columns:
            output[column] = pd.to_numeric(output[column], errors="coerce").round(2)

    output = output.astype(object).where(pd.notna(output), None)
    return output.to_dict(orient="records")


def build_summary(gaps: pd.DataFrame) -> list[dict]:
    if gaps.empty:
        return []

    summary = (
        gaps.groupby("gap_type", as_index=False)
        .agg(
            count=("transaction_id", "count"),
            total_exposure=("exposure_amount", "sum"),
        )
        .sort_values(by="gap_type")
    )
    summary["total_exposure"] = summary["total_exposure"].round(2)
    return _frame_to_records(summary)


def build_report(txns: pd.DataFrame, stls: pd.DataFrame) -> dict:
    gaps = run_reconciliation(txns, stls)
    return {
        "gaps": _frame_to_records(gaps[REPORT_COLUMNS + ["exposure_amount"]] if not gaps.empty else gaps),
        "summary": build_summary(gaps),
        "total_gaps": int(len(gaps)),
    }


def save_report(report: dict, destination: str | Path) -> None:
    Path(destination).write_text(json.dumps(report, indent=2), encoding="utf-8")
