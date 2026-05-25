# Customer Segmentation Dashboard

A machine learning project for customer segmentation, churn prediction, and RFM analysis using e-commerce data.

## Features

- **Churn Prediction**: ML models to identify at-risk customers
- **RFM Analysis**: Recency, Frequency, Monetary segmentation
- **Data Analysis**: EDA and business insights
- **Dashboard**: Interactive visualization powered by Power BI
- **PostgreSQL Integration**: Data persistence and querying

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL

### Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the analysis pipeline:

```bash
python churn_ml.py              # Train ML models
python rfm_analysis_and_segmentation.py  # Generate RFM segments
python business_insights_roi.py # Calculate ROI insights
```

View the dashboard:
- Open `index.html` in a browser for the web dashboard
- Open `analytics.pbix` in Power BI for detailed analytics

## Project Structure

- `churn_*.py` - Churn data processing and ML models
- `rfm_analysis_and_segmentation.py` - Customer segmentation
- `exploratory_data_analysis.py` - Data exploration
- `import_data_to_postgresql.py` - Database setup
- `analytics.pbix` - Power BI dashboard
- `data/` - Raw and processed datasets

## License

MIT
