"""Load and clean UN Comtrade CSV downloads.

Raw files live in data/raw and follow the naming convention
    <reporter>_<flow>_<partner>_hs<code>_<year>.csv
e.g. us_imports_china_hs61_2025.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .paths import PROCESSED_DIR, RAW_DIR

# Columns we keep from the Comtrade export, renamed to short snake_case names.
KEEP = {
    "period": "period",
    "refYear": "year",
    "refMonth": "month",
    "reporterISO": "reporter",
    "flowDesc": "flow",
    "partnerISO": "partner",
    "partnerDesc": "partner_name",
    "cmdCode": "hs_code",
    "cmdDesc": "hs_desc",
    "qtyUnitAbbr": "qty_unit",
    "qty": "qty",
    "netWgt": "net_kg",
    "cifvalue": "cif_usd",
    "fobvalue": "fob_usd",
    "primaryValue": "value_usd",
}


def read_comtrade(path: Path) -> pd.DataFrame:
    """Read one Comtrade CSV and return a tidy frame."""
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={"cmdCode": str})
    df = df[list(KEEP)].rename(columns=KEEP)
    # Monthly files have period like 202501; annual files have 2025.
    period = df["period"].astype(str)
    fmt = "%Y%m" if period.str.len().eq(6).all() else "%Y"
    df["date"] = pd.to_datetime(period, format=fmt)
    if fmt == "%Y":
        df["month"] = pd.NA  # annual rows have no month
    # Comtrade writes 0 when quantity/weight is not reported.
    for col in ("qty", "net_kg"):
        df[col] = df[col].where(df[col] > 0)
    df["source_file"] = path.name
    return df


def load(pattern: str = "us_imports_china_hs61_*.csv") -> pd.DataFrame:
    """Load every raw file matching `pattern` into one monthly frame."""
    files = sorted(RAW_DIR.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files match {pattern} in {RAW_DIR}")
    df = pd.concat([read_comtrade(f) for f in files], ignore_index=True)
    key = ["date", "reporter", "flow", "partner", "hs_code"]
    dupes = df.duplicated(key)
    if dupes.any():
        raise ValueError(f"Duplicate rows for {key}: {df[dupes][key].to_dict('records')}")
    return df.sort_values(key).reset_index(drop=True)


def build_processed(pattern: str = "us_imports_china_hs61_*.csv",
                    out_name: str = "us_imports_china_hs61_monthly.csv") -> Path:
    """Load raw files and write the combined monthly table to data/processed."""
    df = load(pattern)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / out_name
    df.to_csv(out, index=False)
    return out
