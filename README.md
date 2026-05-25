# 📊 Customer Segmentation & Churn Analysis Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/)

A comprehensive **end-to-end customer analytics platform** featuring RFM segmentation, machine learning-based churn prediction, and interactive business intelligence dashboards. Built on the **Olist Brazilian E-Commerce Dataset** with 99K+ customers.

🔗 **[Live Dashboard](https://arnavmodi-msit.github.io/Customer-Segmentation-Dashboard/#dashboard)** | 📁 **[GitHub Repo](https://github.com/ArnavModi-MSIT/-Customer-Segmentation-Dashboard-)**

---

## 🎯 Project Objectives

- **Segment customers** using RFM (Recency, Frequency, Monetary) analysis into 6 actionable groups
- **Predict customer churn** using machine learning models (Logistic Regression, Random Forest, Gradient Boosting)
- **Identify high-value customers** for targeted retention campaigns
- **Calculate ROI metrics** for business decision-making
- **Visualize insights** through interactive Power BI dashboards and web interface

---

## ✨ Key Features

### 📈 Customer Segmentation
- **6 Customer Segments**: Champions, Loyal Customers, Potential Loyalists, Need Attention, At Risk, Lost Customers
- **RFM Analysis**: Data-driven segmentation based on Recency, Frequency, and Monetary value
- **Actionable Insights**: Tailored strategies for each segment

### 🔮 Churn Prediction
- **ML-Powered Models**: Logistic Regression, Random Forest, Gradient Boosting
- **Risk Scoring**: Identify at-risk customers before they leave
- **Feature Engineering**: 25+ engineered features for accurate predictions

### 📊 Business Analytics
- **Key Metrics**: 99K+ total customers, 12K champion customers, 48% revenue contribution
- **Interactive Dashboard**: Real-time Power BI visualizations
- **ROI Insights**: Revenue opportunity analysis and retention metrics

### 🛠 Technical Stack
- **Data Processing**: Python, Pandas, NumPy
- **Machine Learning**: Scikit-learn, XGBoost
- **Database**: PostgreSQL with SQL optimization
- **Visualization**: Power BI, HTML/CSS
- **Analytics**: RFM segmentation algorithms, statistical analysis

---

## 📦 Dataset

**Olist Brazilian E-Commerce Dataset** - Public marketplace data from 2016-2018
- **100,000+** orders
- **32,000+** products
- **99,000+** unique customers
- **50+ features** across multiple dimensions (customers, orders, products, reviews, payments)
- **Geolocation data** for Brazilian cities

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Virtual environment tool (venv or conda)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ArnavModi-MSIT/-Customer-Segmentation-Dashboard-.git
cd Customer-Segmentation-Dashboard
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure PostgreSQL**
```bash
# Update database credentials in import_data_to_postgresql.py
# Default: localhost, port 5432, database: olist_db
```

### 📊 Running the Analysis Pipeline

```bash
# Step 1: Import data to PostgreSQL
python import_data_to_postgresql.py

# Step 2: Process churn data
python churn_data.py

# Step 3: Train churn prediction models
python churn_ml.py

# Step 4: Generate RFM segments
python rfm_analysis_and_segmentation.py

# Step 5: Calculate business ROI insights
python business_insights_roi.py

# Step 6: Exploratory Data Analysis
python exploratory_data_analysis.py
```

### 📈 Viewing Results

- **Web Dashboard**: Open `index.html` in your browser
  ```bash
  # On Windows
  start index.html
  # On macOS
  open index.html
  # On Linux
  xdg-open index.html
  ```

- **Power BI Dashboard**: Open `analytics.pbix` in Microsoft Power BI Desktop
- **CSV Results**: Check generated CSV files for detailed segment and prediction data

---

## 🔍 Key Results & Insights

### Customer Segments
| Segment | Count | %Total | Avg Value | Strategy |
|---------|-------|--------|-----------|----------|
| Champions | 12,000 | 12% | High | Nurture & Retention |
| Loyal Customers | 15,000 | 15% | Medium-High | Engagement Programs |
| Potential Loyalists | 18,000 | 18% | Medium | Convert to Loyal |
| Need Attention | 25,000 | 25% | Low-Medium | Reactivation |
| At Risk | 18,000 | 18% | Low | Win-back Campaigns |
| Lost Customers | 11,000 | 12% | Very Low | Not Profitable |

### Performance Metrics
- **Churn Prediction Accuracy**: ~85-90% (varies by model)
- **Revenue Concentration**: Top 12% of customers = 48% of revenue
- **Retention Opportunity**: 31% of customers need engagement
- **At-Risk Customers**: 18% requiring immediate attention

---

## 🛠 Technologies Used

### Data Processing & ML
- **Pandas** (1.3+) - Data manipulation and analysis
- **NumPy** (1.20+) - Numerical computing
- **Scikit-learn** (0.24+) - Machine learning models
- **XGBoost** (1.3+) - Gradient boosting

### Database & SQL
- **PostgreSQL** (12+) - Relational database
- **psycopg2** (2.8+) - PostgreSQL adapter for Python

### Visualization & BI
- **Power BI** - Interactive business dashboards
- **Matplotlib** (3.3+) - Statistical plots
- **Seaborn** (0.11+) - Visualization library

### Web & Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with gradients & animations
- **Responsive Design** - Mobile-first approach

---

## 📚 Usage Examples

### Run specific analysis
```bash
# Only RFM analysis
python rfm_analysis_and_segmentation.py

# Only churn predictions
python churn_ml.py

# Only ROI calculations
python business_insights_roi.py
```

### Database queries
```bash
# Connect to PostgreSQL and explore data
psql -U postgres -d olist_db

# Example query: Top 10 products by revenue
SELECT * FROM order_items ORDER BY price DESC LIMIT 10;
```

### Export results
CSV files are automatically generated in the project root:
- `customer_churn_predictions.csv` - Churn predictions for all customers
- `rfm_analysis_results.csv` - Detailed RFM analysis
- `segment_summary.csv` - Segment summaries and metrics

---

## 🔐 Security & Best Practices

- **Never commit** sensitive files (database credentials, passwords)
- **Use environment variables** for configuration (see `.env.example`)
- **Database access** requires local PostgreSQL setup
- **Git history** contains project evolution and commits
- **Code is production-ready** with error handling and logging

---

## 📈 Model Details

### Churn Prediction Models
1. **Logistic Regression** - Baseline model for interpretability
2. **Random Forest** - Ensemble method with feature importance
3. **Gradient Boosting (XGBoost)** - Advanced model for accuracy

### Features Engineering
- **Recency**: Days since last purchase
- **Frequency**: Total number of purchases
- **Monetary**: Total spending amount
- **Time-series features**: Purchase trends, seasonality
- **Customer lifecycle**: Account age, status
- **Behavioral indicators**: Product categories, order patterns

---

## 📊 Methodology

### RFM Segmentation Process
1. **Calculate RFM Scores**: Quintile-based scoring (1-5) for each metric
2. **Segment Mapping**: Combine scores to create 6 segments
3. **Business Rules**: Apply domain knowledge for segment names
4. **Actionable Insights**: Develop strategies for each segment

### ML Pipeline
1. **Data Preparation**: Cleaning, encoding, scaling
2. **Feature Engineering**: Creating predictive features
3. **Train/Test Split**: 80/20 cross-validation
4. **Model Training**: Hyperparameter tuning with GridSearch
5. **Evaluation**: Accuracy, precision, recall, F1-score
6. **Prediction**: Score all customers for churn risk

---

## 📝 License

This project is licensed under the **MIT License**

---

## 👤 Author & Contact

**Arnav Modi**
- GitHub: [@ArnavModi-MSIT](https://github.com/ArnavModi-MSIT)
- Project: [Customer Segmentation Dashboard](https://arnavmodi-msit.github.io/Customer-Segmentation-Dashboard/)
