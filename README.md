# Customer Segmentation & Churn Analysis Dashboard

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

End-to-end customer analytics platform built on the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Segments 99K+ customers using RFM analysis, predicts churn with XGBoost (89.2% accuracy), and surfaces insights through a RAG-powered AI assistant and interactive Power BI dashboards.

**[Live Dashboard](https://arnavmodi-msit.github.io/Customer-Segmentation-Dashboard/) · [AI Assistant](https://darkthanos-customer-insights-assistant.hf.space) · [GitHub](https://github.com/ArnavModi-MSIT/-Customer-Segmentation-Dashboard-)**

---

## Results

| Metric | Value |
|--------|-------|
| Customers segmented | 99,000+ |
| Churn prediction accuracy | 89.2% |
| High-risk customers identified | 10,000+ |
| Revenue at risk flagged | ₹1.57M |
| Champion segment revenue share | 48% |

---

## Features

**RFM Segmentation**
Customers scored on Recency, Frequency, and Monetary value and mapped to 6 segments: Champions, Loyal Customers, Potential Loyalists, Need Attention, At Risk, Lost. Each segment includes targeted retention strategies.

**Churn Prediction**
XGBoost model trained on 25+ engineered features including purchase trends, RFM scores, and behavioral indicators. Identifies at-risk customers before churn occurs.

**AI Customer Insights Assistant**
RAG pipeline built with LangChain, ChromaDB, and Gemini 2.5 Flash. Answers natural language business questions grounded in segment data and churn reports. Deployed on Hugging Face Spaces and embedded in the dashboard.

**Power BI Dashboard**
Interactive visualizations covering segment distribution, churn probability by spending tier, and revenue recovery scenarios.

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data processing | Python, Pandas, NumPy, PostgreSQL |
| Machine learning | Scikit-learn, XGBoost |
| RAG pipeline | LangChain, ChromaDB, Gemini 2.5 Flash |
| Visualization | Power BI, HTML/CSS |
| Deployment | GitHub Pages, Hugging Face Spaces |

---

## Project Structure

```
├── import_data_to_postgresql.py   # Load Olist dataset into PostgreSQL
├── churn_data.py                  # Feature engineering for churn model
├── churn_ml.py                    # Train and evaluate churn models
├── rfm_analysis_and_segmentation.py  # RFM scoring and segmentation
├── business_insights_roi.py       # ROI and revenue opportunity analysis
├── generate_knowledge_base.py     # Build RAG knowledge base documents
├── create_vector_db.py            # Embed documents into ChromaDB
├── rag_pipeline.py                # CLI RAG query interface
├── app.py                         # Streamlit RAG web interface
├── index.html / style.css         # Portfolio dashboard
├── analytics.pbix                 # Power BI report
└── knowledge_base/                # Segment and churn documents
```

---

## Setup

**Prerequisites:** Python 3.8+, PostgreSQL 12+

```bash
git clone https://github.com/ArnavModi-MSIT/-Customer-Segmentation-Dashboard-.git
cd Customer-Segmentation-Dashboard
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

**Run the pipeline:**
```bash
python import_data_to_postgresql.py
python churn_data.py
python churn_ml.py
python rfm_analysis_and_segmentation.py
python business_insights_roi.py
python generate_knowledge_base.py
python create_vector_db.py
```

**Query via CLI:**
```bash
python rag_pipeline.py
```

**Run Streamlit UI:**
```bash
streamlit run app.py
```

---

## Dataset

[Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — public marketplace data from 2016–2018.
100K+ orders · 99K+ customers · 32K+ products · 50+ features across orders, payments, reviews, and geolocation.

---

## Author

**Arnav Modi**
GitHub: [@ArnavModi-MSIT](https://github.com/ArnavModi-MSIT)
