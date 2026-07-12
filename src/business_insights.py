import pandas as pd
from datetime import datetime


def load_and_merge(features_path="outputs/customer_churn_features.csv",
                    predictions_path="outputs/customer_churn_predictions.csv"):
    df_features = pd.read_csv(features_path)
    df_predictions = pd.read_csv(predictions_path)
    # FIXED: merge key was 'customer_id' (doesn't exist in either file anymore) —
    # both files key on customer_unique_id since the identity fix.
    df = df_features.merge(
        df_predictions[["customer_unique_id", "churn_probability", "churn_risk"]],
        on="customer_unique_id",
    )
    return df


def spending_segment_analysis(df):
    df = df.copy()
    df["spending_segment"] = pd.cut(
        df["monetary_value"], bins=[0, 100, 300, 10000], labels=["Low Value", "Medium Value", "High Value"]
    )
    result = df.groupby("spending_segment", observed=True).agg(
        customer_count=("customer_unique_id", "count"),
        avg_churn_probability=("churn_probability", "mean"),
        total_revenue=("monetary_value", "sum"),
        avg_rating=("avg_review_score", "mean"),
    ).round(2)
    result["churn_rate_pct"] = (result["avg_churn_probability"] * 100).round(2)
    return df, result


def risk_segment_analysis(df):
    return df.groupby("churn_risk", observed=True).agg(
        customer_count=("customer_unique_id", "count"),
        total_revenue=("monetary_value", "sum"),
        avg_customer_value=("monetary_value", "mean"),
        avg_rating=("avg_review_score", "mean"),
        avg_recency=("recency_days", "mean"),
    ).round(2)


def key_insights(df):
    high_risk = df[df["churn_risk"] == "High"]
    medium_risk = df[df["churn_risk"] == "Medium"]
    low_risk = df[df["churn_risk"] == "Low"]

    insights = {
        "high_risk_count": len(high_risk),
        "high_risk_revenue": high_risk["monetary_value"].sum(),
        "high_risk_avg_value": high_risk["monetary_value"].mean(),
        "high_risk_avg_rating": high_risk["avg_review_score"].mean(),
        "medium_risk_count": len(medium_risk),
        "low_risk_count": len(low_risk),
    }

    if len(high_risk) and len(low_risk):
        insights["rating_ratio_low_vs_high"] = (
            low_risk["avg_review_score"].mean() / high_risk["avg_review_score"].mean()
        )
        insights["rating_diff_low_vs_high"] = (
            low_risk["avg_review_score"].mean() - high_risk["avg_review_score"].mean()
        )

    return insights, high_risk, medium_risk, low_risk


def roi_scenarios(df, high_risk, medium_risk, retention_rates=(10, 20, 30)):
    current_revenue = df["monetary_value"].sum()
    high_risk_revenue = high_risk["monetary_value"].sum()
    medium_risk_revenue = medium_risk["monetary_value"].sum()

    scenarios = []
    for rate in retention_rates:
        recovered = (high_risk_revenue * rate) / 100
        scenarios.append({
            "retention_rate_pct": rate,
            "recovered_revenue": round(recovered, 2),
            "growth_pct": round((recovered / current_revenue) * 100, 2),
        })

    rating_improvement_recovery = high_risk_revenue * 0.15

    return {
        "current_revenue": current_revenue,
        "high_risk_revenue": high_risk_revenue,
        "medium_risk_revenue": medium_risk_revenue,
        "retention_scenarios": scenarios,
        "rating_improvement_recovery_estimate": round(rating_improvement_recovery, 2),
    }


def run_business_insights(verbose=True,
                           features_path="outputs/customer_churn_features.csv",
                           predictions_path="outputs/customer_churn_predictions.csv"):
    df = load_and_merge(features_path, predictions_path)
    df, spending_summary = spending_segment_analysis(df)
    risk_summary = risk_segment_analysis(df)
    insights, high_risk, medium_risk, low_risk = key_insights(df)
    roi = roi_scenarios(df, high_risk, medium_risk)

    if verbose:
        print("=" * 80)
        print("CHURN ANALYSIS — BUSINESS INSIGHTS & ROI")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print("\n1. CHURN RATE BY SPENDING SEGMENT")
        print(spending_summary.to_string())
        print("\n2. CHURN RATE BY RISK SEGMENT")
        print(risk_summary.to_string())
        print("\n3. KEY INSIGHTS")
        print(f"  High-risk customers: {insights['high_risk_count']:,}")
        print(f"  High-risk revenue: R$ {insights['high_risk_revenue']:,.2f}")
        if "rating_ratio_low_vs_high" in insights:
            print(f"  Low-risk rating is {insights['rating_ratio_low_vs_high']:.2f}x higher than high-risk")
        print("\n4. ROI SCENARIOS")
        print(f"  Current revenue: R$ {roi['current_revenue']:,.2f}")
        for s in roi["retention_scenarios"]:
            print(f"  Retain {s['retention_rate_pct']}% of high-risk: +R$ {s['recovered_revenue']:,.2f} "
                  f"({s['growth_pct']}% growth)")
        print("=" * 80)

    return {
        "spending_summary": spending_summary,
        "risk_summary": risk_summary,
        "insights": insights,
        "roi": roi,
    }


if __name__ == "__main__":
    run_business_insights()
