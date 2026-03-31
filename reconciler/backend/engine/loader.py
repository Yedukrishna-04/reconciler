from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

TRANSACTION_REQUIRED_COLUMNS = {
    "transaction_id",
    "customer_id",
    "amount",
    "currency",
    "created_at",
    "status",
    "type",
}

SETTLEMENT_REQUIRED_COLUMNS = {
    "settlement_id",
    "transaction_id",
    "settled_amount",
    "settled_at",
    "bank_reference",
}


def _ensure_columns(df: pd.DataFrame, required: set[str], label: str) -> pd.DataFrame:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")
    return df


def _load_csv(source: str | Path | bytes, parse_dates: list[str]) -> pd.DataFrame:
    if isinstance(source, (str, Path)):
        return pd.read_csv(source, parse_dates=parse_dates)
    return pd.read_csv(io.BytesIO(source), parse_dates=parse_dates)


def load_transactions(path: str | Path) -> pd.DataFrame:
    df = _load_csv(path, parse_dates=["created_at"])
    _ensure_columns(df, TRANSACTION_REQUIRED_COLUMNS, "transactions.csv")
    df["amount"] = pd.to_numeric(df["amount"], errors="raise").round(2)
    return df


def load_settlements(path: str | Path) -> pd.DataFrame:
    df = _load_csv(path, parse_dates=["settled_at"])
    _ensure_columns(df, SETTLEMENT_REQUIRED_COLUMNS, "settlements.csv")
    df["settled_amount"] = pd.to_numeric(df["settled_amount"], errors="raise").round(2)
    return df


def load_transactions_from_bytes(payload: bytes) -> pd.DataFrame:
    df = _load_csv(payload, parse_dates=["created_at"])
    _ensure_columns(df, TRANSACTION_REQUIRED_COLUMNS, "uploaded transactions file")
    df["amount"] = pd.to_numeric(df["amount"], errors="raise").round(2)
    return df


def load_settlements_from_bytes(payload: bytes) -> pd.DataFrame:
    df = _load_csv(payload, parse_dates=["settled_at"])
    _ensure_columns(df, SETTLEMENT_REQUIRED_COLUMNS, "uploaded settlements file")
    df["settled_amount"] = pd.to_numeric(df["settled_amount"], errors="raise").round(2)
    return df
