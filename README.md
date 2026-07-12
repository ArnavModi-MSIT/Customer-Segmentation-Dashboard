# Customer Segmentation & Churn Risk Analysis

End-to-end analytics pipeline on the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): RFM customer segmentation and XGBoost-based churn risk scoring, orchestrated in Python, stored in PostgreSQL, and visualized in Power BI.

**[Live Dashboard](#)** · **[Power BI Report](#)**

---

## Overview

- **96,096** unique customers analyzed across 99,441 orders
- **7-segment RFM model** (Champions, Loyal Customers, Potential Loyalist, At Risk, Need Attention, New Customers, Lost)
- **XGBoost churn risk model** scoring customers by likelihood of inactivity
- **3-page Power BI dashboard**, fully driven by PostgreSQL

## Key Findings

| Metric | Value |
|---|---|
| Champions revenue share | 13.15% (from 6.96% of customers) |
| Repeat purchase rate | 3.12% |
| High-risk revenue at stake | R$1.03M |
| Low-risk vs. high-risk review rating | 1.23x higher |
| Churn model ROC-AUC | 0.65 |

Customer purchase behavior in this dataset is heavily one-time-buyer skewed, which shapes the segmentation: "Need Attention" is the largest single segment, and review score emerges as the strongest behavioral signal for churn risk — customers who rate their experience lower are meaningfully more likely to be flagged high-risk.

## Architecture

```
CSV files → PostgreSQL (ingestion) → EDA → RFM segmentation
                                         → Churn feature engineering → XGBoost → risk scoring
                                         → Business insights / ROI
                                                    ↓
                                    PostgreSQL (results tables) → Power BI
```

## Tech Stack

Python · Pandas · Scikit-learn · XGBoost · PostgreSQL · SQLAlchemy · Power BI

## Project Structure

```
├── config.py                  # env-based config
├── run_pipeline.py            # single entrypoint, runs all stages in order
├── inspect_data.py            # raw CSV schema/quality checker (run before ingestion)
├── src/
│   ├── db.py                  # shared Postgres engine
│   ├── ingestion.py           # raw CSVs → Postgres, product category cleanup
│   ├── eda.py                 # revenue/order/customer/review metrics
│   ├── rfm.py                 # RFM scoring + 7-segment classification
│   ├── churn_features.py      # customer-level churn feature engineering
│   ├── churn_model.py         # XGBoost training + risk scoring
│   ├── churn_writeback.py     # predictions → Postgres
│   └── business_insights.py   # ROI scenarios, risk-segment analysis
├── scripts/
│   ├── index.html             # project landing page
│   └── style.css
├── dashboards/
│   └── analytics.pbix
└── outputs/                   # generated CSVs
```

## Running It

```bash
pip install -r requirements.txt
# create .env with DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
python inspect_data.py         # verify raw data before touching the DB
python run_pipeline.py         # ingestion → EDA → RFM → churn → insights
```

Each stage can also be run independently, e.g. `python src/eda.py`.