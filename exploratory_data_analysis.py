import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# PostgreSQL connection
username = "postgres"
password = "root"
host = "localhost"
port = "5432"
database = "olist_project"

engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")

print("="*80)
print("OLIST E-COMMERCE EXPLORATORY DATA ANALYSIS (EDA)")
print("="*80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1. LOAD DATA FROM POSTGRESQL
# ============================================================================
print("📊 LOADING DATA FROM POSTGRESQL...")
print("-"*80)

try:
    customers_df = pd.read_sql("SELECT * FROM olist_customers_dataset", engine)
    orders_df = pd.read_sql("SELECT * FROM olist_orders_dataset", engine)
    order_items_df = pd.read_sql("SELECT * FROM olist_order_items_dataset", engine)
    products_df = pd.read_sql("SELECT * FROM olist_products_dataset", engine)
    reviews_df = pd.read_sql("SELECT * FROM olist_order_reviews_dataset", engine)
    sellers_df = pd.read_sql("SELECT * FROM olist_sellers_dataset", engine)
    payments_df = pd.read_sql("SELECT * FROM olist_order_payments_dataset", engine)
    
    print(f"✓ Customers: {len(customers_df):,} records")
    print(f"✓ Orders: {len(orders_df):,} records")
    print(f"✓ Order Items: {len(order_items_df):,} records")
    print(f"✓ Products: {len(products_df):,} records")
    print(f"✓ Reviews: {len(reviews_df):,} records")
    print(f"✓ Sellers: {len(sellers_df):,} records")
    print(f"✓ Payments: {len(payments_df):,} records")
    
except Exception as e:
    print(f"❌ Error loading data: {str(e)}")
    exit()

# ============================================================================
# 2. DATA OVERVIEW
# ============================================================================
print("\n" + "="*80)
print("1. DATA OVERVIEW")
print("="*80)

# Basic statistics
print("\n📌 DATASET DIMENSIONS:")
print(f"  Customers: {customers_df.shape}")
print(f"  Orders: {orders_df.shape}")
print(f"  Order Items: {order_items_df.shape}")
print(f"  Products: {products_df.shape}")
print(f"  Reviews: {reviews_df.shape}")

# ============================================================================
# 3. MISSING VALUES ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("2. MISSING VALUES ANALYSIS")
print("="*80)

def check_missing_values(df, name):
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"\n📌 {name}:")
        for col in missing[missing > 0].index:
            pct = (missing[col] / len(df)) * 100
            print(f"  {col}: {missing[col]:,} ({pct:.2f}%)")
    else:
        print(f"\n✓ {name}: No missing values")

check_missing_values(customers_df, "Customers")
check_missing_values(orders_df, "Orders")
check_missing_values(order_items_df, "Order Items")
check_missing_values(products_df, "Products")
check_missing_values(reviews_df, "Reviews")

# ============================================================================
# 4. KEY METRICS
# ============================================================================
print("\n" + "="*80)
print("3. KEY BUSINESS METRICS")
print("="*80)

# Merge dataframes for analysis
orders_items = orders_df.merge(order_items_df, on='order_id', how='inner')
orders_full = orders_items.merge(customers_df, on='customer_id', how='inner')

# Numeric columns fix
orders_full['price'] = pd.to_numeric(orders_full['price'], errors='coerce')
orders_full['freight_value'] = pd.to_numeric(orders_full['freight_value'], errors='coerce')
orders_full['total_value'] = orders_full['price'] + orders_full['freight_value']

print(f"\n💰 REVENUE METRICS:")
total_revenue = orders_full[orders_full['order_status'] == 'delivered']['total_value'].sum()
print(f"  Total Revenue: R$ {total_revenue:,.2f}")
print(f"  Average Order Value: R$ {orders_full[orders_full['order_status'] == 'delivered']['total_value'].mean():,.2f}")
print(f"  Median Order Value: R$ {orders_full[orders_full['order_status'] == 'delivered']['total_value'].median():,.2f}")
print(f"  Min Order Value: R$ {orders_full[orders_full['order_status'] == 'delivered']['total_value'].min():,.2f}")
print(f"  Max Order Value: R$ {orders_full[orders_full['order_status'] == 'delivered']['total_value'].max():,.2f}")

print(f"\n📦 ORDER METRICS:")
total_orders = len(orders_df)
delivered_orders = len(orders_df[orders_df['order_status'] == 'delivered'])
canceled_orders = len(orders_df[orders_df['order_status'] == 'canceled'])
print(f"  Total Orders: {total_orders:,}")
print(f"  Delivered Orders: {delivered_orders:,} ({(delivered_orders/total_orders)*100:.1f}%)")
print(f"  Canceled Orders: {canceled_orders:,} ({(canceled_orders/total_orders)*100:.1f}%)")
print(f"  Average Items per Order: {len(order_items_df) / total_orders:.2f}")

print(f"\n👥 CUSTOMER METRICS:")
print(f"  Total Unique Customers: {customers_df['customer_id'].nunique():,}")
print(f"  Total Unique States: {customers_df['customer_state'].nunique()}")
print(f"  Total Unique Cities: {customers_df['customer_city'].nunique():,}")

repeat_customers = orders_df.groupby('customer_id').size()
repeat_rate = (len(repeat_customers[repeat_customers > 1]) / len(customers_df)) * 100
print(f"  Repeat Purchase Rate: {repeat_rate:.2f}%")
print(f"  Avg Orders per Customer: {len(orders_df) / len(customers_df):.2f}")

# ============================================================================
# 5. TEMPORAL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("4. TEMPORAL ANALYSIS")
print("="*80)

# Convert dates
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['year'] = orders_df['order_purchase_timestamp'].dt.year
orders_df['month'] = orders_df['order_purchase_timestamp'].dt.month
orders_df['date'] = orders_df['order_purchase_timestamp'].dt.date

print(f"\n📅 DATE RANGE:")
print(f"  Start Date: {orders_df['order_purchase_timestamp'].min()}")
print(f"  End Date: {orders_df['order_purchase_timestamp'].max()}")
print(f"  Duration: {(orders_df['order_purchase_timestamp'].max() - orders_df['order_purchase_timestamp'].min()).days} days")

# ============================================================================
# 6. GEOGRAPHIC ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("5. GEOGRAPHIC ANALYSIS")
print("="*80)

print(f"\n🗺️ TOP 10 STATES BY CUSTOMER COUNT:")
top_states = customers_df['customer_state'].value_counts().head(10)
for i, (state, count) in enumerate(top_states.items(), 1):
    pct = (count / len(customers_df)) * 100
    print(f"  {i}. {state}: {count:,} customers ({pct:.1f}%)")

# ============================================================================
# 7. PRODUCT ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("6. PRODUCT ANALYSIS")
print("="*80)

products_full = order_items_df.merge(products_df, on='product_id', how='left')
products_full['price'] = pd.to_numeric(products_full['price'], errors='coerce')

print(f"\n📦 PRODUCT METRICS:")
print(f"  Total Unique Products: {products_df['product_id'].nunique():,}")
print(f"  Total Categories: {products_df['product_category_name'].nunique()}")

print(f"\n🏆 TOP 10 CATEGORIES BY REVENUE:")
top_categories = products_full.groupby('product_category_name')['price'].sum().nlargest(10)
for i, (category, revenue) in enumerate(top_categories.items(), 1):
    print(f"  {i}. {category}: R$ {revenue:,.2f}")

# ============================================================================
# 8. REVIEW ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("7. REVIEW ANALYSIS")
print("="*80)

reviews_df['review_score'] = pd.to_numeric(reviews_df['review_score'], errors='coerce')

print(f"\n⭐ REVIEW METRICS:")
print(f"  Total Reviews: {len(reviews_df):,}")
print(f"  Average Rating: {reviews_df['review_score'].mean():.2f} / 5.0")
print(f"  Median Rating: {reviews_df['review_score'].median():.2f}")
print(f"  Std Dev: {reviews_df['review_score'].std():.2f}")

print(f"\n📊 RATING DISTRIBUTION:")
rating_dist = reviews_df['review_score'].value_counts().sort_index()
for rating, count in rating_dist.items():
    pct = (count / len(reviews_df)) * 100
    bar = "█" * int(pct/2)
    print(f"  {rating} stars: {count:6,} ({pct:5.1f}%) {bar}")

# ============================================================================
# 9. PAYMENT ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("8. PAYMENT ANALYSIS")
print("="*80)

print(f"\n💳 PAYMENT METHODS:")
payment_methods = payments_df['payment_type'].value_counts()
for method, count in payment_methods.items():
    pct = (count / len(payments_df)) * 100
    print(f"  {method.upper()}: {count:,} ({pct:.1f}%)")

print(f"\n💰 INSTALLMENT ANALYSIS:")
installments = payments_df[payments_df['payment_installments'] > 0]['payment_installments'].value_counts().nlargest(5)
print(f"  Top Installment Options:")
for installment, count in installments.items():
    pct = (count / len(payments_df[payments_df['payment_installments'] > 0])) * 100
    print(f"    {int(installment)} installments: {count:,} ({pct:.1f}%)")

# ============================================================================
# 10. DATA QUALITY SUMMARY
# ============================================================================
print("\n" + "="*80)
print("9. DATA QUALITY SUMMARY")
print("="*80)

print(f"\n✅ DATA QUALITY CHECKS:")
print(f"  ✓ No duplicate customer IDs: {customers_df['customer_id'].duplicated().sum() == 0}")
print(f"  ✓ No duplicate order IDs: {orders_df['order_id'].duplicated().sum() == 0}")
print(f"  ✓ Prices are positive: {(order_items_df['price'] > 0).all()}")
print(f"  ✓ Freight values are positive: {(order_items_df['freight_value'] >= 0).all()}")
print(f"  ✓ Valid review scores (1-5): {reviews_df['review_score'].between(1, 5).all()}")

# ============================================================================
# 11. SUMMARY STATISTICS TABLE
# ============================================================================
print("\n" + "="*80)
print("10. SUMMARY STATISTICS")
print("="*80)

summary_table = pd.DataFrame({
    'Metric': [
        'Total Revenue (R$)',
        'Total Orders',
        'Total Customers',
        'Total Products',
        'Total Reviews',
        'Average Order Value (R$)',
        'Repeat Purchase Rate (%)',
        'Delivery Success Rate (%)',
        'Average Review Score'
    ],
    'Value': [
        f"{total_revenue:,.2f}",
        f"{total_orders:,}",
        f"{len(customers_df):,}",
        f"{products_df['product_id'].nunique():,}",
        f"{len(reviews_df):,}",
        f"{orders_full[orders_full['order_status'] == 'delivered']['total_value'].mean():,.2f}",
        f"{repeat_rate:.2f}",
        f"{(delivered_orders/total_orders)*100:.2f}",
        f"{reviews_df['review_score'].mean():.2f}"
    ]
})

print("\n" + summary_table.to_string(index=False))

# ============================================================================
# 12. EXPORT SUMMARY REPORT
# ============================================================================
print("\n" + "="*80)
print("EDA COMPLETE!")
print("="*80)
print("\n📝 NEXT STEPS:")
print("  1. Review the SQL queries in the SQL files")
print("  2. Create cleaned tables using SQL queries")
print("  3. Build Power BI dashboards with KPI data")
print("  4. Perform RFM analysis for customer segmentation")
print("  5. Analyze churn risks and retention rates")
print("\n✅ Ready for advanced analytics!\n")
print("="*80)