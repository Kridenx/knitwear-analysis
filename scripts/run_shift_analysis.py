"""Did US knitwear orders move from China to other countries?

Uses:
  data/raw/us_imports_world_hs61_<year>.csv      (US imports, 7 partners, HS 61 + 6110, monthly)
  data/raw/china_exports_world_hs60_2023_2025.csv (China's knitted-fabric exports, annual)

Run from the project root:
    .venv/bin/python scripts/run_shift_analysis.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from knitwear import load, shift  # noqa: E402
from knitwear.paths import PROCESSED_DIR  # noqa: E402

REPORTS = ROOT / "reports"
FIG = REPORTS / "figures"
FIG.mkdir(parents=True, exist_ok=True)
NAMES = shift.PARTNER_NAMES
COMPETITORS = ["VNM", "KHM", "BGD", "IDN", "IND"]


def main() -> None:
    us = load.load("us_imports_world_hs61_*.csv")
    fabric = load.load("china_exports_world_hs60_*.csv")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    us.to_csv(PROCESSED_DIR / "us_imports_world_hs61_monthly.csv", index=False)
    fabric.to_csv(PROCESSED_DIR / "china_exports_world_hs60_annual.csv", index=False)

    tables = {}
    for code in ["61", "6110"]:
        annual = shift.by_partner(us, code)
        ytd = shift.by_partner(us, code, months=range(1, 9))
        tables[code] = {
            "annual_musd": annual.drop(index=2026),          # 2026 is Jan-Aug only
            "annual_share_pct": shift.shares(annual.drop(index=2026)),
            "ytd_jan_aug_musd": ytd,
            "ytd_jan_aug_share_pct": shift.shares(ytd),
            "change_2024_2025": shift.change(annual, 2024, 2025),
        }

    fabric_tbl = fabric.pivot_table(index="year", columns="partner", values="value_usd") / 1e6
    fabric_idx = shift.index_to_base(fabric_tbl, 2023)

    with pd.ExcelWriter(REPORTS / "shift_summary.xlsx") as xw:
        for code, t in tables.items():
            for name, tbl in t.items():
                tbl.rename(columns=NAMES, index=NAMES).round(1).to_excel(
                    xw, sheet_name=f"hs{code}_{name}"[:31])
        fabric_tbl.rename(columns=NAMES).round(1).to_excel(xw, sheet_name="hs60_cn_exports_musd")
        fabric_idx.rename(columns=NAMES).round(1).to_excel(xw, sheet_name="hs60_index_2023_100")

    # 4. Monthly share of US HS61 imports: China vs competitors
    ms = shift.monthly_share(us, "61")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for p in ["CHN"] + COMPETITORS:
        ax.plot(ms.index, ms[p], label=NAMES[p], lw=2.5 if p == "CHN" else 1.5)
    ax.set_title("Share of US knitted-apparel (HS61) imports, monthly")
    ax.set_ylabel("% of US imports from world")
    ax.legend(ncol=3)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "04_partner_share_monthly.png", dpi=150)

    # 5. Who gained what China lost, 2024 -> 2025
    ch = tables["61"]["change_2024_2025"].drop(index=shift.WORLD)
    ch = ch.loc[["CHN"] + COMPETITORS]
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#c0392b" if v < 0 else "#2e86c1" for v in ch["change_musd"]]
    ax.bar([NAMES[p] for p in ch.index], ch["change_musd"], color=colors)
    for i, v in enumerate(ch["change_musd"]):
        ax.text(i, v, f"{v:+,.0f}", ha="center", va="bottom" if v > 0 else "top", fontsize=9)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title("Change in US HS61 imports, 2025 vs 2024 (USD million)")
    fig.tight_layout()
    fig.savefig(FIG / "05_change_2024_2025.png", dpi=150)

    # 6. China's knitted-fabric (HS60) exports, 2023 = 100
    fig, ax = plt.subplots(figsize=(7, 4))
    for p in ["W00", "VNM", "KHM", "BGD"]:
        ax.plot(fabric_idx.index, fabric_idx[p], marker="o",
                label=NAMES[p], lw=2.5 if p == "W00" else 1.5,
                ls="--" if p == "W00" else "-")
    ax.set_xticks(fabric_idx.index)
    ax.set_title("China's knitted-fabric (HS60) exports, index 2023 = 100")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "06_china_fabric_exports_index.png", dpi=150)

    pd.set_option("display.float_format", "{:,.1f}".format)
    pd.set_option("display.width", 200)
    print("HS61 change 2024 -> 2025:\n", tables["61"]["change_2024_2025"].rename(index=NAMES), "\n")
    print("HS61 annual share %:\n", tables["61"]["annual_share_pct"].rename(columns=NAMES), "\n")
    print("HS6110 change 2024 -> 2025:\n", tables["6110"]["change_2024_2025"].rename(index=NAMES), "\n")
    print("HS60 China fabric exports, 2023=100:\n", fabric_idx.rename(columns=NAMES))


if __name__ == "__main__":
    main()
