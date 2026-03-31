from __future__ import annotations

import pandas as pd

REPORT_COLUMNS = [
    "gap_type",
    "transaction_id",
    "amount",
    "settled_amount",
    "created_at",
    "settled_at",
    "amount_diff",
    "details",
]


def _finalize(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=REPORT_COLUMNS)

    output = frame.copy()
    for column in REPORT_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA

    output["amount"] = pd.to_numeric(output["amount"], errors="coerce").round(2)
    output["settled_amount"] = pd.to_numeric(output["settled_amount"], errors="coerce").round(2)
    output["amount_diff"] = pd.to_numeric(output["amount_diff"], errors="coerce").fillna(0.0).round(2)

    return output[REPORT_COLUMNS]


def detect_late_settlements(txns: pd.DataFrame, stls: pd.DataFrame) -> pd.DataFrame:
    """Settlement month differs from transaction month."""
    merged = txns.merge(stls, on="transaction_id", how="inner")
    mask = merged["settled_at"].dt.to_period("M") != merged["created_at"].dt.to_period("M")
    late = merged.loc[mask, ["transaction_id", "amount", "settled_amount", "created_at", "settled_at"]].copy()
    late["amount_diff"] = 0.0
    late["details"] = late.apply(
        lambda row: (
            f"Transaction created on {row['created_at'].date()} settled on "
            f"{row['settled_at'].date()}, crossing the month boundary."
        ),
        axis=1,
    )
    late["gap_type"] = "late_settlement"
    return _finalize(late)


def detect_rounding_gaps(
    txns: pd.DataFrame,
    stls: pd.DataFrame,
    threshold: float = 0.005,
) -> pd.DataFrame:
    """Settled amount differs from the transaction amount beyond the threshold."""
    merged = txns.merge(stls, on="transaction_id", how="inner")
    merged["amount_diff"] = (merged["settled_amount"] - merged["amount"]).abs()
    mask = merged["amount_diff"] > threshold
    gaps = merged.loc[
        mask,
        ["transaction_id", "amount", "settled_amount", "created_at", "settled_at", "amount_diff"],
    ].copy()
    gaps["details"] = gaps.apply(
        lambda row: (
            f"Transaction amount {row['amount']:.2f} vs settled amount "
            f"{row['settled_amount']:.2f}."
        ),
        axis=1,
    )
    gaps["gap_type"] = "rounding_gap"
    return _finalize(gaps)


def detect_duplicates(txns: pd.DataFrame) -> pd.DataFrame:
    """Duplicate transaction_id rows in the transactions file."""
    dupes = txns.loc[txns.duplicated("transaction_id", keep=False), ["transaction_id", "amount", "created_at"]].copy()
    dupes["settled_amount"] = pd.NA
    dupes["settled_at"] = pd.NaT
    dupes["amount_diff"] = 0.0
    dupes["details"] = dupes["transaction_id"].map(
        lambda transaction_id: f"transaction_id {transaction_id} appears more than once in transactions.csv."
    )
    dupes["gap_type"] = "duplicate"
    return _finalize(dupes)


def detect_orphan_refunds(txns: pd.DataFrame) -> pd.DataFrame:
    """Refund rows with no matching original transaction reference."""
    refunds = txns.loc[txns["type"] == "refund"].copy()
    if refunds.empty:
        return _finalize(refunds)

    originals = set(txns.loc[txns["type"] != "refund", "transaction_id"])
    if "ref_transaction_id" in refunds.columns:
        reference_ids = refunds["ref_transaction_id"].fillna(refunds["transaction_id"])
    else:
        reference_ids = refunds["transaction_id"]

    orphans = refunds.loc[~reference_ids.isin(originals), ["transaction_id", "amount", "created_at"]].copy()
    orphans["settled_amount"] = pd.NA
    orphans["settled_at"] = pd.NaT
    orphans["amount_diff"] = 0.0
    orphans["details"] = orphans["transaction_id"].map(
        lambda transaction_id: f"Refund references unknown original transaction {transaction_id}."
    )
    orphans["gap_type"] = "orphan_refund"
    return _finalize(orphans)
