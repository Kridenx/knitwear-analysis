"""Summary tables for monthly trade data."""
from __future__ import annotations

import pandas as pd


def monthly_wide(df: pd.DataFrame, value: str = "value_usd") -> pd.DataFrame:
    """Months (1-12) as rows, years as columns, values in USD millions."""
    wide = df.pivot_table(index="month", columns="year", values=value, aggfunc="sum")
    return wide / 1e6


def yoy(df: pd.DataFrame, value: str = "value_usd") -> pd.DataFrame:
    """Year-over-year % change for each month."""
    wide = monthly_wide(df, value)
    return wide.pct_change(axis=1, fill_method=None) * 100


def annual_summary(df: pd.DataFrame, value: str = "value_usd") -> pd.DataFrame:
    """Full-year and same-period (year-to-date) totals per year.

    YTD uses the months available in the latest year, so a partial year
    can be compared fairly with earlier ones.
    """
    latest = df["year"].max()
    ytd_months = sorted(df.loc[df["year"] == latest, "month"].unique())
    g = df.groupby("year")
    out = pd.DataFrame({
        "months": g["month"].nunique(),
        "total_musd": g[value].sum() / 1e6,
        f"ytd_m{ytd_months[0]}-{ytd_months[-1]}_musd":
            df[df["month"].isin(ytd_months)].groupby("year")[value].sum() / 1e6,
    })
    ytd_col = out.columns[-1]
    out["ytd_yoy_pct"] = out[ytd_col].pct_change() * 100
    out.loc[out["months"] < 12, "total_musd"] = float("nan")  # not comparable
    return out


def seasonal_share(df: pd.DataFrame, value: str = "value_usd") -> pd.DataFrame:
    """Each month's share of its year's total (full years only), in %."""
    full = df.groupby("year")["month"].transform("nunique") == 12
    d = df[full]
    share = d[value] / d.groupby("year")[value].transform("sum") * 100
    return d.assign(share=share).pivot_table(index="month", columns="year", values="share")
