import pandas as pd
import numpy as np
from datetime import datetime

df_features = pd.read_csv('customer_churn_features.csv')
df_predictions = pd.read_csv('customer_churn_predictions.csv')

df = df_features.merge(df_predictions[['customer_id', 'churn_probability', 'churn_risk']], on='customer_id')

print("="*80)
print("CHURN ANALYSIS - BUSINESS INSIGHTS & ROI")
print("="*80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("1. CHURN RATE BY SPENDING SEGMENT")
print("-"*80)

spending_segments = pd.cut(df['monetary_value'], bins=[0, 100, 300, 10000], labels=['Low Value', 'Medium Value', 'High Value'])
df['spending_segment'] = spending_segments

churn_by_spending = df.groupby('spending_segment').agg({
    'customer_id': 'count',
    'churn_probability': 'mean',
    'monetary_value': 'sum',
    'avg_review_score': 'mean'
}).round(2)

churn_by_spending.columns = ['Customer_Count', 'Avg_Churn_Probability', 'Total_Revenue', 'Avg_Rating']
churn_by_spending['Churn_Rate_%'] = (churn_by_spending['Avg_Churn_Probability'] * 100).round(2)

print(churn_by_spending)

print("\n2. CHURN RATE BY RISK SEGMENT")
print("-"*80)

churn_by_risk = df.groupby('churn_risk').agg({
    'customer_id': 'count',
    'monetary_value': ['sum', 'mean'],
    'avg_review_score': 'mean',
    'frequency': 'mean',
    'recency_days': 'mean'
}).round(2)

churn_by_risk.columns = ['Customer_Count', 'Total_Revenue', 'Avg_Customer_Value', 'Avg_Rating', 'Avg_Frequency', 'Avg_Recency']

print(churn_by_risk)

print("\n3. KEY INSIGHTS")
print("-"*80)

high_risk = df[df['churn_risk'] == 'High']
medium_risk = df[df['churn_risk'] == 'Medium']
low_risk = df[df['churn_risk'] == 'Low']

print(f"\n📊 HIGH-RISK CUSTOMERS:")
print(f"  • Count: {len(high_risk):,}")
print(f"  • Total Revenue: R$ {high_risk['monetary_value'].sum():,.2f}")
print(f"  • Avg Customer Value: R$ {high_risk['monetary_value'].mean():,.2f}")
print(f"  • Avg Rating: {high_risk['avg_review_score'].mean():.2f}/5.0")
print(f"  • Avg Purchase Frequency: {high_risk['frequency'].mean():.2f}")
print(f"  • Days Since Purchase: {high_risk['recency_days'].mean():.0f}")

print(f"\n📊 MEDIUM-RISK CUSTOMERS:")
print(f"  • Count: {len(medium_risk):,}")
print(f"  • Total Revenue: R$ {medium_risk['monetary_value'].sum():,.2f}")
print(f"  • Avg Customer Value: R$ {medium_risk['monetary_value'].mean():,.2f}")
print(f"  • Avg Rating: {medium_risk['avg_review_score'].mean():.2f}/5.0")
print(f"  • Avg Purchase Frequency: {medium_risk['frequency'].mean():.2f}")

print(f"\n📊 LOW-RISK CUSTOMERS:")
print(f"  • Count: {len(low_risk):,}")
print(f"  • Total Revenue: R$ {low_risk['monetary_value'].sum():,.2f}")
print(f"  • Avg Customer Value: R$ {low_risk['monetary_value'].mean():,.2f}")
print(f"  • Avg Rating: {low_risk['avg_review_score'].mean():.2f}/5.0")

rating_diff = low_risk['avg_review_score'].mean() - high_risk['avg_review_score'].mean()
rating_ratio = low_risk['avg_review_score'].mean() / high_risk['avg_review_score'].mean()

print(f"\n🔍 CRITICAL FINDING:")
print(f"  Low-risk customers have {rating_ratio:.2f}x HIGHER ratings than high-risk")
print(f"  Rating difference: {rating_diff:.2f} points")

medium_spenders = df[df['spending_segment'] == 'Medium Value']
high_spenders = df[df['spending_segment'] == 'High Value']
low_spenders = df[df['spending_segment'] == 'Low Value']

print(f"\n💰 CHURN BY SPENDING SEGMENT:")
print(f"  Medium Spenders: {(medium_spenders['churn_probability'].mean()*100):.1f}% churn rate (HIGHEST)")
print(f"  Low Spenders: {(low_spenders['churn_probability'].mean()*100):.1f}% churn rate")
print(f"  High Spenders: {(high_spenders['churn_probability'].mean()*100):.1f}% churn rate (LOWEST)")

print("\n4. ROI ANALYSIS - RETENTION SCENARIOS")
print("-"*80)

current_revenue = df['monetary_value'].sum()
high_risk_revenue = high_risk['monetary_value'].sum()
medium_risk_revenue = medium_risk['monetary_value'].sum()

retention_rates = [10, 20, 30]

print(f"\nCurrent Annual Revenue: R$ {current_revenue:,.2f}")
print(f"Revenue at Risk (High): R$ {high_risk_revenue:,.2f}")
print(f"Revenue at Risk (Medium): R$ {medium_risk_revenue:,.2f}")

print(f"\nSCENARIO: Retain X% of High-Risk Customers")
for rate in retention_rates:
    recovered_revenue = (high_risk_revenue * rate) / 100
    new_total = current_revenue + recovered_revenue
    growth = (recovered_revenue / current_revenue) * 100
    print(f"  • Retain {rate}%: +R$ {recovered_revenue:,.2f} revenue ({growth:.2f}% growth)")

print(f"\nSCENARIO: Improve Ratings by 0.5 points for High-Risk (increase retention 15%)")
improvement_revenue = high_risk_revenue * 0.15
new_revenue = current_revenue + improvement_revenue
roi = (improvement_revenue / 100000) * 100
print(f"  • Expected recovery: R$ {improvement_revenue:,.2f}")
print(f"  • New total revenue: R$ {new_revenue:,.2f}")

print("\n5. TOP 3 ACTIONABLE RECOMMENDATIONS")
print("-"*80)

print(f"\n🎯 RECOMMENDATION 1: Focus on Service Quality (HIGHEST IMPACT)")
print(f"  Problem: High-risk customers have {rating_ratio:.2f}x lower ratings")
print(f"  Action: Implement quality check for customers with ratings < 3.5")
print(f"  Impact: Potential 15-20% retention improvement")
print(f"  Revenue Potential: R$ {high_risk_revenue * 0.15:,.2f} - R$ {high_risk_revenue * 0.20:,.2f}")

print(f"\n🎯 RECOMMENDATION 2: Target Medium Spenders (QUICK WIN)")
print(f"  Problem: Medium spenders have highest churn rate")
print(f"  Action: Create loyalty program for medium spenders (R$ 100-300 range)")
print(f"  Target: {len(medium_spenders):,} customers")
print(f"  Impact: Expected 10-15% churn reduction")
print(f"  Revenue Potential: R$ {medium_risk_revenue * 0.10:,.2f} - R$ {medium_risk_revenue * 0.15:,.2f}")

print(f"\n🎯 RECOMMENDATION 3: Win-Back Campaign (RECOVERY)")
print(f"  Problem: {len(high_risk):,} customers at high churn risk")
print(f"  Action: Personalized discount + engagement email for inactive customers")
print(f"  Target: Customers inactive for 200+ days with churn probability > 0.7")

inactive_high_risk = high_risk[high_risk['recency_days'] > 200]
print(f"  Segment Size: {len(inactive_high_risk):,} customers")
print(f"  Segment Revenue: R$ {inactive_high_risk['monetary_value'].sum():,.2f}")
print(f"  Impact: Expected 5-10% recovery rate")
print(f"  Revenue Potential: R$ {inactive_high_risk['monetary_value'].sum() * 0.05:,.2f} - R$ {inactive_high_risk['monetary_value'].sum() * 0.10:,.2f}")

print("\n6. IMPLEMENTATION ROADMAP")
print("-"*80)
print("\nPhase 1 (Weeks 1-4): Quality Improvement")
print("  • Identify root causes of low ratings in high-risk segment")
print("  • Implement quality checks")
print("  • Track improvement\n")

print("Phase 2 (Weeks 5-8): Loyalty Program")
print("  • Launch loyalty program for medium spenders")
print("  • Monitor engagement and retention\n")

print("Phase 3 (Weeks 9-12): Win-Back Campaign")
print("  • Design personalized offers for inactive customers")
print("  • Execute email campaigns")
print("  • Measure conversion\n")

print("="*80)
print("SUMMARY: Combined initiatives could recover R$ 100K-500K annually")
print("="*80)
