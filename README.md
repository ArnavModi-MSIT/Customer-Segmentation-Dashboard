# Customer Segmentation & Churn Risk Analysis

End-to-end analytics pipeline on the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): RFM customer segmentation and XGBoost-based churn risk scoring, orchestrated in Python, stored in PostgreSQL, and visualized in Power BI.

**[Live Dashboard](#)** · **[Power BI Report](#)**

---

## Overview

- **96,096** unique customers analyzed (99,441 orders)
- **7-segment RFM model** (Champions, Loyal, Potential Loyalist, At Risk, Need Attention, New, Lost)
- **XGBoost churn risk model** — ROC-AUC 0.65
- **3-page Power BI dashboard**, fully driven by PostgreSQL, no manual CSV wiring

## Key Findings

| Metric | Value |
|---|---|
| Champions revenue share | 13.15% (of 6.96% of customers) |
| Repeat purchase rate | 3.12% |
| High-risk revenue at stake | R$1.03M |
| Low-risk vs. high-risk review rating | 1.23x higher |
| Churn model ROC-AUC | 0.65 |

**The dataset's own structure shapes the story:** 97% of customers place exactly one order. This means "churn" here is largely a recency signal rather than a repeat-purchase behavior pattern — the churn model reflects that honestly (ROC-AUC 0.65, not an inflated accuracy number) rather than overclaiming predictive power the data doesn't support.

## Data Correctness

This project went through a full audit and rebuild after the original pipeline produced numbers that didn't hold up under verification. Three bugs were significant enough to change every downstream metric:

1. **Wrong customer identity.** Olist's `customer_id` is a per-order surrogate key — every order gets a unique one, so grouping by it makes every customer look like a one-time buyer by construction. The real identity is `customer_unique_id`. This alone changed customer counts from 99,441 to 96,096 and made repeat-purchase rate calculable at all (previously showed 0%).
2. **Order-value aggregation bug.** Revenue/order-value stats were computed on `order_items` rows without first aggregating to one row per order. ~10% of orders have multiple items, so multi-item orders were being double- or triple-counted in average order value.
3. **Merge fan-out in churn features.** `order_items` and `payments` were joined onto `orders` independently via separate `order_id` merges — for an order with 2 items and a 2-installment payment, this silently produced a 4-row cartesian blow-up, inflating monetary features for exactly those customers.

Each fix was verified against the raw CSVs directly (`inspect_data.py`) before being applied to the pipeline, not just assumed correct from code review.

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
└── outputs/                   # generated CSVs (committed for visibility)
```

## Running It

```bash
pip install -r requirements.txt
# create .env with DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
python inspect_data.py         # verify raw data before touching the DB
python run_pipeline.py         # ingestion → EDA → RFM → churn → insights
```

Each stage can also be run independently for debugging, e.g. `python src/eda.py`.
