"""Trade-shift analysis: where did US orders go when China's share fell?

Works on the multi-partner files (us_imports_world_hs61_<year>.csv), where
partner "W00" is the world total.
"""
from __future__ import annotations

import pandas as pd

WORLD = "W00"
PARTNER_NAMES = {
    "W00": "World", "CHN": "China", "VNM": "Vietnam", "BGD": "Bangladesh",
    "KHM": "Cambodia", "IND": "India", "IDN": "Indonesia",
}


def by_partner(df: pd.DataFrame, hs_code: str, months: list[int] | None = None) -> pd.DataFrame:
    """Yearly import value (USD million), years as rows, partners as columns.

    Pass `months` (e.g. range(1, 9)) to compare the same period across years.
    """
    d = df[df["hs_code"] == hs_code]
    if months is not None:
        d = d[d["month"].isin(list(months))]
    return d.pivot_table(index="year", columns="partner", values="value_usd", aggfunc="sum") / 1e6


def shares(table: pd.DataFrame) -> pd.DataFrame:
    """Each partner's share of the world total, in %."""
    return table.div(table[WORLD], axis=0).drop(columns=WORLD) * 100


def change(table: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    """Change in USD million and % between two years, one row per partner.

    `covers_china_loss_pct` says how much of China's lost value each
    partner picked up (positive = gained what China lost).
    """
    diff = table.loc[end] - table.loc[start]
    out = pd.DataFrame({
        f"{start}_musd": table.loc[start],
        f"{end}_musd": table.loc[end],
        "change_musd": diff,
        "change_pct": diff / table.loc[start] * 100,
    })
    china_loss = -diff["CHN"]
    out["covers_china_loss_pct"] = diff / china_loss * 100
    out.loc[["CHN", WORLD], "covers_china_loss_pct"] = float("nan")
    return out.sort_values("change_musd")


def monthly_share(df: pd.DataFrame, hs_code: str) -> pd.DataFrame:
    """Monthly share of world total for each partner, in %. Dates as rows."""
    d = df[df["hs_code"] == hs_code]
    wide = d.pivot_table(index="date", columns="partner", values="value_usd", aggfunc="sum")
    return shares(wide)


def index_to_base(table: pd.DataFrame, base_year: int) -> pd.DataFrame:
    """Rescale each column so base_year = 100 (to compare growth rates)."""
    return table / table.loc[base_year] * 100
