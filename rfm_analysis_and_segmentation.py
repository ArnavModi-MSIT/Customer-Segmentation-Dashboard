import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# PostgreSQL connection
username = "postgres"
password = "root"
host = "localhost"
port = "5432"
database = "olist_project"

engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")

print("="*80)
print("RFM ANALYSIS - CUSTOMER SEGMENTATION")
print("="*80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("📊 LOADING DATA...")
print("-"*80)

try:
    customers_df = pd.read_sql("SELECT * FROM olist_customers_dataset", engine)
    orders_df = pd.read_sql("SELECT * FROM olist_orders_dataset", engine)
    order_items_df = pd.read_sql("SELECT * FROM olist_order_items_dataset", engine)
    reviews_df = pd.read_sql("SELECT * FROM olist_order_reviews_dataset", engine)
    
    print("✓ Data loaded successfully")
except Exception as e:
    print(f"❌ Error loading data: {str(e)}")
    exit()

# ============================================================================
# 2. PREPARE DATA FOR RFM
# ============================================================================
print("\n📋 PREPARING DATA FOR RFM ANALYSIS...")
print("-"*80)

# Convert dates
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])

# Merge data
order_items_df['price'] = pd.to_numeric(order_items_df['price'], errors='coerce')
order_items_df['freight_value'] = pd.to_numeric(order_items_df['freight_value'], errors='coerce')
order_items_df['total_value'] = order_items_df['price'] + order_items_df['freight_value']

orders_full = orders_df.merge(order_items_df, on='order_id', how='inner')
orders_full = orders_full.merge(customers_df[['customer_id', 'customer_state']], on='customer_id', how='left')
orders_full = orders_full.merge(reviews_df[['order_id', 'review_score']], on='order_id', how='left')

# Filter only delivered orders
orders_delivered = orders_full[orders_full['order_status'] == 'delivered'].copy()

print(f"✓ Total transactions: {len(orders_delivered):,}")
print(f"✓ Unique customers: {orders_delivered['customer_id'].nunique():,}")

# ============================================================================
# 3. CALCULATE RFM METRICS
# ============================================================================
print("\n📊 CALCULATING RFM METRICS...")
print("-"*80)

# Analysis date (maximum date in dataset + 1)
analysis_date = orders_delivered['order_purchase_timestamp'].max() + timedelta(days=1)
print(f"Analysis Date: {analysis_date.date()}")

# RFM Calculation
rfm = orders_delivered.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (analysis_date - x.max()).days,  # Recency
    'order_id': 'count',  # Frequency
    'total_value': 'sum',  # Monetary
    'review_score': 'mean'  # Average review score
}).reset_index()

rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary', 'avg_rating']

# Merge with customer state
rfm = rfm.merge(customers_df[['customer_id', 'customer_state']], on='customer_id', how='left')

print(f"✓ RFM calculated for {len(rfm):,} customers")

# ============================================================================
# 4. RFM STATISTICS
# ============================================================================
print("\n📈 RFM STATISTICS")
print("-"*80)

print(f"\n💰 RECENCY (Days since last purchase):")
print(f"  Mean: {rfm['recency'].mean():.1f} days")
print(f"  Median: {rfm['recency'].median():.1f} days")
print(f"  Min: {rfm['recency'].min():.0f} days")
print(f"  Max: {rfm['recency'].max():.0f} days")
print(f"  Std Dev: {rfm['recency'].std():.1f} days")

print(f"\n📦 FREQUENCY (Number of purchases):")
print(f"  Mean: {rfm['frequency'].mean():.2f}")
print(f"  Median: {rfm['frequency'].median():.1f}")
print(f"  Min: {rfm['frequency'].min():.0f}")
print(f"  Max: {rfm['frequency'].max():.0f}")
print(f"  Std Dev: {rfm['frequency'].std():.2f}")

print(f"\n💵 MONETARY (Total spending in R$):")
print(f"  Mean: R$ {rfm['monetary'].mean():,.2f}")
print(f"  Median: R$ {rfm['monetary'].median():,.2f}")
print(f"  Min: R$ {rfm['monetary'].min():,.2f}")
print(f"  Max: R$ {rfm['monetary'].max():,.2f}")
print(f"  Std Dev: R$ {rfm['monetary'].std():,.2f}")

# ============================================================================
# 5. RFM SCORING
# ============================================================================
print("\n🎯 ASSIGNING RFM SCORES (1-5 scale)...")
print("-"*80)

# Recency: Lower is better (recently purchased)
rfm['R_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')

# Frequency: Higher is better (more purchases)
rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Monetary: Higher is better (more spending)
rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

# Convert to numeric
rfm['R_score'] = pd.to_numeric(rfm['R_score'])
rfm['F_score'] = pd.to_numeric(rfm['F_score'])
rfm['M_score'] = pd.to_numeric(rfm['M_score'])

# Overall RFM score
rfm['RFM_Score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']
rfm['RFM_Score_Avg'] = rfm['RFM_Score'] / 3

print(f"✓ RFM Scores assigned (1-5 for each dimension)")
print(f"✓ Overall RFM Score range: 3-15")

# ============================================================================
# 6. CUSTOMER SEGMENTATION
# ============================================================================
print("\n👥 CUSTOMER SEGMENTATION LOGIC...")
print("-"*80)

def segment_customer(row):
    r, f, m = row['R_score'], row['F_score'], row['M_score']
    
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 4 and f >= 3 and m >= 3:
        return 'Loyal Customers'
    elif r >= 3 and f >= 1 and m >= 3:
        return 'Potential Loyalist'
    elif r >= 4 and f <= 2 and m <= 2:
        return 'New Customers'
    elif r <= 2 and f >= 3 and m >= 3:
        return 'At Risk'
    elif r <= 1 and f <= 2 and m <= 2:
        return 'Lost'
    else:
        return 'Need Attention'

rfm['Segment'] = rfm.apply(segment_customer, axis=1)

print("✓ 6 Customer Segments created:")
print("  1. Champions - Best customers (high R,F,M)")
print("  2. Loyal Customers - Regular buyers")
print("  3. Potential Loyalist - High value but declining frequency")
print("  4. New Customers - Recent but low frequency")
print("  5. At Risk - Previously good, now inactive")
print("  6. Lost - Very inactive and low value")
print("  7. Need Attention - Others")

# ============================================================================
# 7. SEGMENT ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("SEGMENT ANALYSIS")
print("="*80)

segment_analysis = rfm.groupby('Segment').agg({
    'customer_id': 'count',
    'recency': 'mean',
    'frequency': 'mean',
    'monetary': 'mean',
    'avg_rating': 'mean',
    'RFM_Score_Avg': 'mean'
}).round(2)

segment_analysis.columns = ['Customer_Count', 'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Avg_Rating', 'Avg_RFM_Score']
segment_analysis = segment_analysis.sort_values('Avg_RFM_Score', ascending=False)

# Add percentage
total_customers = len(rfm)
segment_analysis['Percentage'] = (segment_analysis['Customer_Count'] / total_customers * 100).round(2)
segment_analysis['Revenue_Share'] = (rfm.groupby('Segment')['monetary'].sum() / rfm['monetary'].sum() * 100).round(2)

print("\n" + segment_analysis.to_string())

# ============================================================================
# 8. DETAILED SEGMENT METRICS
# ============================================================================
print("\n" + "="*80)
print("DETAILED SEGMENT BREAKDOWN")
print("="*80)

for segment in ['Champions', 'Loyal Customers', 'Potential Loyalist', 'New Customers', 'At Risk', 'Lost']:
    segment_data = rfm[rfm['Segment'] == segment]
    if len(segment_data) == 0:
        continue
    
    print(f"\n🔹 {segment}")
    print("-"*80)
    print(f"  Customer Count: {len(segment_data):,} ({len(segment_data)/total_customers*100:.1f}%)")
    print(f"  Total Revenue: R$ {segment_data['monetary'].sum():,.2f}")
    print(f"  Avg Customer Value: R$ {segment_data['monetary'].mean():,.2f}")
    print(f"  Avg Recency: {segment_data['recency'].mean():.0f} days")
    print(f"  Avg Frequency: {segment_data['frequency'].mean():.2f} purchases")
    print(f"  Avg Rating: {segment_data['avg_rating'].mean():.2f} / 5.0")
    print(f"  Revenue Share: {segment_data['monetary'].sum()/rfm['monetary'].sum()*100:.1f}%")
    
    # Top states
    top_states = segment_data['customer_state'].value_counts().head(3)
    print(f"  Top States: {', '.join([f'{state}({count})' for state, count in top_states.items()])}")

# ============================================================================
# 9. BUSINESS INSIGHTS
# ============================================================================
print("\n" + "="*80)
print("KEY BUSINESS INSIGHTS")
print("="*80)

champions = rfm[rfm['Segment'] == 'Champions']
at_risk = rfm[rfm['Segment'] == 'At Risk']
lost = rfm[rfm['Segment'] == 'Lost']

print(f"\n💎 CHAMPIONS (Best Customers):")
if len(champions) > 0:
    champions_revenue_share = champions['monetary'].sum() / rfm['monetary'].sum() * 100
    print(f"  • {len(champions):,} customers ({len(champions)/total_customers*100:.1f}% of base)")
    print(f"  • Generate R$ {champions['monetary'].sum():,.2f} ({champions_revenue_share:.1f}% of revenue)")
    print(f"  • Average Value: R$ {champions['monetary'].mean():,.2f}")
    print(f"  • Average Rating: {champions['avg_rating'].mean():.2f}/5.0")
    print(f"  👉 ACTION: Reward loyalty, exclusive offers, priority support")

print(f"\n⚠️ AT RISK (Churn Prevention):")
if len(at_risk) > 0:
    at_risk_revenue_share = at_risk['monetary'].sum() / rfm['monetary'].sum() * 100
    print(f"  • {len(at_risk):,} customers ({len(at_risk)/total_customers*100:.1f}% of base)")
    print(f"  • Previously generated R$ {at_risk['monetary'].sum():,.2f} ({at_risk_revenue_share:.1f}% of revenue)")
    print(f"  • Inactive for avg {at_risk['recency'].mean():.0f} days")
    print(f"  👉 ACTION: Win-back campaigns, special discounts, re-engagement")

print(f"\n💔 LOST (Reactivation):")
if len(lost) > 0:
    lost_revenue_share = lost['monetary'].sum() / rfm['monetary'].sum() * 100
    print(f"  • {len(lost):,} customers ({len(lost)/total_customers*100:.1f}% of base)")
    print(f"  • Previously generated R$ {lost['monetary'].sum():,.2f} ({lost_revenue_share:.1f}% of revenue)")
    print(f"  • Very inactive ({lost['recency'].mean():.0f} days)")
    print(f"  👉 ACTION: Reactivation campaigns, clear inventory offers")

print(f"\n🌟 PARETO PRINCIPLE (80/20 RULE):")
# Calculate cumulative revenue by RFM score
rfm_sorted = rfm.sort_values('monetary', ascending=False)
rfm_sorted['cumsum_revenue'] = rfm_sorted['monetary'].cumsum()
rfm_sorted['cumsum_pct'] = rfm_sorted['cumsum_revenue'] / rfm['monetary'].sum() * 100

top_20_pct_customers = int(len(rfm) * 0.2)
top_20_revenue = rfm_sorted.iloc[:top_20_pct_customers]['cumsum_pct'].iloc[-1]

print(f"  • Top 20% of customers ({top_20_pct_customers:,}) generate {top_20_revenue:.1f}% of revenue")
print(f"  • Focus on retention over acquisition")
print(f"  • Prioritize Champion and Loyal customer segments")

# ============================================================================
# 10. EXPORT TO CSV
# ============================================================================
print("\n" + "="*80)
print("EXPORTING RESULTS...")
print("="*80)

rfm_export = rfm[['customer_id', 'customer_state', 'recency', 'frequency', 'monetary', 
                   'avg_rating', 'R_score', 'F_score', 'M_score', 'RFM_Score', 'RFM_Score_Avg', 'Segment']]

try:
    rfm_export.to_csv('rfm_analysis_results.csv', index=False)
    print("✓ RFM results exported to 'rfm_analysis_results.csv'")
    
    segment_analysis.to_csv('segment_summary.csv')
    print("✓ Segment summary exported to 'segment_summary.csv'")
except Exception as e:
    print(f"❌ Error exporting: {str(e)}")

# ============================================================================
# 11. SUMMARY
# ============================================================================
print("\n" + "="*80)
print("RFM ANALYSIS COMPLETE!")
print("="*80)
print(f"\n✅ Processed {len(rfm):,} customers")
print(f"✅ Created {len(rfm['Segment'].unique())} customer segments")
print(f"✅ Total revenue analyzed: R$ {rfm['monetary'].sum():,.2f}")
print(f"\n📊 Next Steps:")
print("  1. Use segment information for targeted marketing")
print("  2. Create retention strategies for 'At Risk' customers")
print("  3. Build loyalty programs for 'Champions'")
print("  4. Develop win-back campaigns for 'Lost' customers")
print("  5. Import results to Power BI for visualization")
print("\n" + "="*80)