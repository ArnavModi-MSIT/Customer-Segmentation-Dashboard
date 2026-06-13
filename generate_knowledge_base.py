import pandas as pd
from pathlib import Path
import sys

OUTPUT_DIR = Path("knowledge_base")
OUTPUT_DIR.mkdir(exist_ok=True)

try:
    segment_df = pd.read_csv("segment_summary.csv")
except FileNotFoundError:
    print("Error: segment_summary.csv not found.")
    sys.exit(1)

# Validate required columns
required_cols = ["Segment", "Customer_Count", "Revenue_Share", "Avg_Monetary", 
                 "Avg_Frequency", "Avg_Recency", "Avg_RFM_Score", "Percentage"]
missing_cols = [col for col in required_cols if col not in segment_df.columns]
if missing_cols:
    print(f"Error: Missing columns in segment_summary.csv: {missing_cols}")
    sys.exit(1)

# --------------------------------
# Segment Documents
# --------------------------------

for _, row in segment_df.iterrows():
    segment_name = row["Segment"]
    
    document = f"""Segment Name: {segment_name}

Customer Count: {int(row['Customer_Count'])}
Revenue Share: {row['Revenue_Share']:.1f}%
Percentage of Customers: {row['Percentage']:.1f}%

Average Monetary Value: ₹{row['Avg_Monetary']:.2f}
Average Purchase Frequency: {row['Avg_Frequency']:.2f}
Average Recency: {row['Avg_Recency']:.1f} days
Average RFM Score: {row['Avg_RFM_Score']:.1f}

Business Insight:
The {segment_name} segment contributes {row['Revenue_Share']:.1f}% of total revenue
and represents {row['Percentage']:.1f}% of all customers.

Recommended Actions:
"""

    recommendations = {
        "Champions": [
            "Reward loyalty",
            "Early access campaigns",
            "Premium membership programs"
        ],
        "Loyal Customers": [
            "Upsell premium products",
            "Referral programs",
            "Personalized recommendations"
        ],
        "Potential Loyalists": [
            "Targeted promotions",
            "Loyalty incentives",
            "Increase engagement"
        ],
        "At Risk": [
            "Win-back campaigns",
            "Discount offers",
            "Personalized outreach"
        ],
        "Need Attention": [
            "Re-engagement emails",
            "Special promotions"
        ],
        "New Customers": [
            "Onboarding campaigns",
            "First-purchase incentives"
        ],
        "Lost": [
            "Reactivation campaigns",
            "Feedback collection"
        ]
    }

    for item in recommendations.get(segment_name, []):
        document += f"\n- {item}"

    filename = (
        segment_name.lower()
        .replace(" ", "_")
        .replace("/", "_")
    )

    with open(
        OUTPUT_DIR / f"{filename}.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(document)

# --------------------------------
# Churn Report
# --------------------------------

try:
    churn_df = pd.read_csv("customer_churn_predictions.csv")
    
    if "churn_probability" not in churn_df.columns:
        print("Warning: churn_probability column not found. Skipping churn report.")
    else:
        total_customers = len(churn_df)
        high_risk = len(churn_df[churn_df["churn_probability"] >= 0.7])
        medium_risk = len(churn_df[(churn_df["churn_probability"] >= 0.4) & (churn_df["churn_probability"] < 0.7)])
        low_risk = len(churn_df[churn_df["churn_probability"] < 0.4])
        avg_prob = churn_df["churn_probability"].mean()

        report = f"""Customer Churn Risk Report

Total Customers: {total_customers}

High Risk (>=0.7): {high_risk}
Medium Risk (0.4-0.7): {medium_risk}
Low Risk (<0.4): {low_risk}

Average Churn Probability: {avg_prob:.2f}

Business Impact:
High-risk customers should be prioritized for retention campaigns and targeted offers.
"""

        with open(OUTPUT_DIR / "churn_risk_report.txt", "w", encoding="utf-8") as f:
            f.write(report)

except FileNotFoundError:
    print("Warning: customer_churn_predictions.csv not found. Skipping churn report.")
except Exception as e:
    print(f"Warning: Error generating churn report: {e}")

print(f"Knowledge base documents created in {OUTPUT_DIR}")