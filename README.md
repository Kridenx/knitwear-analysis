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
cd ~/knitwear-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```
