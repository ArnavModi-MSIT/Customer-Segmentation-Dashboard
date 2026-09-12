# Customer Segmentation & Sales Analytics Dashboard

An analytics pipeline on the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce):
RFM customer segmentation and sales/product/geography analytics, built with
Python + pandas and visualized in Power BI. No database, no ML — raw CSVs go
in, a clean Excel workbook comes out, and that workbook is the single source
Power BI reads from.

**[Live Preview Dashboard](https://claude.ai/code/artifact/2bbd994f-825a-4324-8dd7-9cc6a1559240)** · **[Power BI Report](#)**

---

## Overview

- **96,096** unique customers analyzed across 99,441 orders
- **7-segment RFM model** (Champions, Loyal Customers, Potential Loyalist, At Risk, Need Attention, New Customers, Lost) — rule-based scoring, not ML
- **4-page Power BI dashboard**: Executive Overview, Customer/RFM Segmentation, Product & Category Performance, Geography
- Entire pipeline runs on a laptop with no server: `pip install`, run one script, open Power BI

## Key Findings

| Metric | Value |
|---|---|
| Total revenue (delivered orders) | R$15.4M |
| Champions revenue share | 13.15% (from 6.96% of customers) |
| Repeat purchase rate | 3.05% |
| Revenue at risk (At Risk + Need Attention + Lost) | R$7.0M (45.6% of total) |
| Recoverable revenue at 20% At Risk retention | +R$641K |

Customer purchase behavior in this dataset is heavily one-time-buyer skewed,
which shapes the segmentation: "Need Attention" is the largest single segment
at ~40% of customers. That single fact — most customers don't come back — is
the central story the dashboard is built to surface.

## Architecture

```
Raw Olist CSVs (data/raw/)
        │
        ▼
  Python: clean, join, RFM-score  (pandas only — no DB, no ML)
        │
        ▼
  Excel workbook (data/processed/olist_analytics.xlsx)
        │
        ▼
  Power BI Desktop: relationships, DAX measures, 4-page report
```

RFM segmentation is rule-based (quantile buckets + threshold rules on
recency/frequency/monetary) — a real analytics technique companies use, not
machine learning. There's no predictive model anywhere in this project by
design; see [docs/POWER_BI_GUIDE.md](docs/POWER_BI_GUIDE.md) for why and how
that changes the retention-ROI framing.

## Tech Stack

Python · Pandas · openpyxl · Power BI · DAX

## Project Structure

```
├── run_pipeline.py            # single entrypoint, runs all stages in order
├── inspect_data.py            # raw CSV schema/quality checker (run before anything else)
├── src/
│   ├── prepare_data.py        # raw CSVs → cleaned, joined star-schema tables (pandas)
│   ├── eda.py                 # revenue/order/customer/review metrics
│   ├── rfm.py                 # RFM scoring + 7-segment classification
│   ├── business_insights.py   # revenue concentration, at-risk revenue, retention scenarios
│   └── export_to_excel.py     # writes every table to one Excel workbook
├── data/
│   ├── raw/                   # source CSVs (gitignored — see "Running It")
│   └── processed/             # olist_analytics.xlsx — the Power BI data source (gitignored)
├── docs/
│   ├── index.html             # project landing page
│   ├── style.css
│   └── POWER_BI_GUIDE.md      # step-by-step: build the report from the Excel workbook
├── analytics.pbix             # Power BI report file
└── outputs/                   # generated CSVs (rfm_analysis_results, segment_summary)
```

## Running It

```bash
pip install -r requirements.txt
```

Download the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
from Kaggle and place all 9 CSVs in `data/raw/`, then:

```bash
python inspect_data.py         # sanity-check the raw files
python run_pipeline.py         # prepare_data → eda → rfm → business_insights → export_to_excel
```

That produces `data/processed/olist_analytics.xlsx`. Open Power BI Desktop
and follow [docs/POWER_BI_GUIDE.md](docs/POWER_BI_GUIDE.md) to build the
report against it — no `.env`, no database, no credentials anywhere in this
project.

Each stage can also be run independently, e.g. `python src/eda.py`.
