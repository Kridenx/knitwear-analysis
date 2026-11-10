"""First-pass analysis of US imports of knitted apparel (HS61) from China.

Run from the project root:
    .venv/bin/python scripts/run_hs61_analysis.py
Outputs go to data/processed and reports/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from knitwear import analysis, load  # noqa: E402

REPORTS = ROOT / "reports"
FIG = REPORTS / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def main() -> None:
    out = load.build_processed()
    df = pd.read_csv(out, parse_dates=["date"])

    wide = analysis.monthly_wide(df)
    yoy = analysis.yoy(df)
    annual = analysis.annual_summary(df)
    season = analysis.seasonal_share(df)

    with pd.ExcelWriter(REPORTS / "hs61_summary.xlsx") as xw:
        annual.round(1).to_excel(xw, sheet_name="annual")
        wide.round(1).to_excel(xw, sheet_name="monthly_musd")
        yoy.round(1).to_excel(xw, sheet_name="monthly_yoy_pct")
        season.round(1).to_excel(xw, sheet_name="seasonal_share_pct")

    # 1. Monthly time series
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["date"], df["value_usd"] / 1e6, marker="o", ms=3)
    ax.set_title("US imports of knitted apparel (HS61) from China, monthly")
    ax.set_ylabel("USD million")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "01_monthly_series.png", dpi=150)

    # 2. Same month, different years
    fig, ax = plt.subplots(figsize=(10, 4))
    for year in wide.columns:
        ax.plot(wide.index, wide[year], marker="o", ms=3, label=str(year))
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("Month")
    ax.set_ylabel("USD million")
    ax.set_title("HS61 imports from China by month, year over year")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "02_by_month_years.png", dpi=150)

    # 3. YTD totals
    ytd_col = [c for c in annual.columns if c.startswith("ytd_m")][0]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(annual.index.astype(str), annual[ytd_col])
    ax.set_title(f"Same-period total ({ytd_col.split('_')[1]})")
    ax.set_ylabel("USD million")
    fig.tight_layout()
    fig.savefig(FIG / "03_ytd_totals.png", dpi=150)

    pd.set_option("display.float_format", "{:,.1f}".format)
    print("Annual summary (USD million):\n", annual, "\n")
    print("Monthly YoY %:\n", yoy, "\n")
    print(f"Wrote {out.relative_to(ROOT)}, reports/hs61_summary.xlsx, reports/figures/*.png")


if __name__ == "__main__":
    main()
