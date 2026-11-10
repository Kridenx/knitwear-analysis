# 针织品出口分析 (Knitwear Export Analysis)

针织品出口数据研究的分析代码。

## 目录结构

```
knitwear-analysis/
├── data/
│   ├── raw/          # 原始数据（不纳入 git）
│   └── processed/    # 清洗后的数据（不纳入 git）
├── notebooks/        # Jupyter 探索性分析
├── src/knitwear/     # 可复用的 Python 代码
├── requirements.txt
└── README.md
```

## 快速开始

```bash
cd ~/"Claude Folder"/knitwear-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

## 运行第一版分析

```bash
.venv/bin/python scripts/run_hs61_analysis.py
```

输出：
- `data/processed/us_imports_china_hs61_monthly.csv`：合并后的月度数据
- `reports/hs61_summary.xlsx`：年度/同期汇总、月度金额、月度同比、季节占比
- `reports/figures/`：月度走势、按月对比、同期总额图

## 数据命名规则

`<报告国>_<流向>_<伙伴>_hs<编码>_<年份>.csv`，例如 `us_imports_china_hs61_2025.csv`。
数据来源：UN Comtrade（https://comtradeplus.un.org）。

## 订单转移分析

```bash
.venv/bin/python scripts/run_shift_analysis.py
```

输出 `reports/shift_summary.xlsx`（各国金额、份额、2024→2025 变化、中国 HS60 面料出口）和 `reports/figures/04–06`。
