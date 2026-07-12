import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")


def load_rfm_source_data(engine):
    customers = pd.read_sql("SELECT customer_id, customer_unique_id, customer_state FROM customers", engine)
    orders = pd.read_sql(
        "SELECT order_id, customer_id, order_status, order_purchase_timestamp FROM orders", engine
    )
    order_items = pd.read_sql("SELECT order_id, price, freight_value FROM order_items", engine)
    reviews = pd.read_sql("SELECT order_id, review_score FROM reviews", engine)
    return customers, orders, order_items, reviews


def build_order_level_table(customers, orders, order_items, reviews):
    """
    Aggregates order_items to ONE ROW PER ORDER first (fixes the frequency-
    inflation bug where multi-item orders were counted multiple times),
    then attaches customer_unique_id (true customer identity, not the
    per-order customer_id) and review score.
    """
    order_items = order_items.copy()
    order_items["price"] = pd.to_numeric(order_items["price"], errors="coerce")
    order_items["freight_value"] = pd.to_numeric(order_items["freight_value"], errors="coerce")
    order_items["total_value"] = order_items["price"] + order_items["freight_value"]

    order_totals = order_items.groupby("order_id")["total_value"].sum().reset_index()

    orders = orders.merge(order_totals, on="order_id", how="inner")  # drops the 775 item-less orders
    orders = orders.merge(customers, on="customer_id", how="left")
    orders = orders.merge(reviews.groupby("order_id")["review_score"].mean().reset_index(), on="order_id", how="left")

    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

    return orders[orders["order_status"] == "delivered"].copy()


def calculate_rfm(orders_delivered):
    analysis_date = orders_delivered["order_purchase_timestamp"].max() + timedelta(days=1)

    rfm = orders_delivered.groupby("customer_unique_id").agg(
        recency=("order_purchase_timestamp", lambda x: (analysis_date - x.max()).days),
        frequency=("order_id", "nunique"),  # FIXED: distinct orders, not item rows
        monetary=("total_value", "sum"),
        avg_rating=("review_score", "mean"),
    ).reset_index()

    # Most-recent state per customer (customers can have multiple recorded states across orders)
    latest_state = (
        orders_delivered.sort_values("order_purchase_timestamp")
        .groupby("customer_unique_id")["customer_state"]
        .last()
        .reset_index()
    )
    rfm = rfm.merge(latest_state, on="customer_unique_id", how="left")

    return rfm, analysis_date


def score_rfm(rfm):
    rfm = rfm.copy()
    rfm["R_score"] = pd.to_numeric(pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop"))
    rfm["F_score"] = pd.to_numeric(
        pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    )
    rfm["M_score"] = pd.to_numeric(
        pd.qcut(rfm["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    )
    rfm["RFM_Score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]
    rfm["RFM_Score_Avg"] = rfm["RFM_Score"] / 3
    return rfm


def segment_customer(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 4 and f >= 3 and m >= 3:
        return "Loyal Customers"
    elif r >= 3 and f >= 1 and m >= 3:
        return "Potential Loyalist"
    elif r >= 4 and f <= 2 and m <= 2:
        return "New Customers"
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    elif r <= 1 and f <= 2 and m <= 2:
        return "Lost"
    else:
        return "Need Attention"


def summarize_segments(rfm):
    summary = rfm.groupby("Segment").agg(
        customer_count=("customer_unique_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_rating=("avg_rating", "mean"),
        avg_rfm_score=("RFM_Score_Avg", "mean"),
    ).round(2)

    total_customers = len(rfm)
    total_revenue = rfm["monetary"].sum()
    summary["pct_of_customers"] = (summary["customer_count"] / total_customers * 100).round(2)
    summary["revenue_share_pct"] = (rfm.groupby("Segment")["monetary"].sum() / total_revenue * 100).round(2)

    return summary.sort_values("avg_rfm_score", ascending=False)


def run_rfm(engine, verbose=True):
    customers, orders, order_items, reviews = load_rfm_source_data(engine)
    orders_delivered = build_order_level_table(customers, orders, order_items, reviews)

    rfm, analysis_date = calculate_rfm(orders_delivered)
    rfm = score_rfm(rfm)
    rfm["Segment"] = rfm.apply(segment_customer, axis=1)

    segment_summary = summarize_segments(rfm)

    if verbose:
        print("=" * 80)
        print("RFM ANALYSIS")
        print("=" * 80)
        print(f"Analysis date: {analysis_date.date()}")
        print(f"Customers analyzed (customer_unique_id): {len(rfm):,}")
        print(f"Max frequency observed: {rfm['frequency'].max()} (sanity check — should be small, not inflated)")
        print()
        print(segment_summary.to_string())
        print("=" * 80)

    return rfm, segment_summary


def write_rfm_to_db(engine, rfm, segment_summary, verbose=True):
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS rfm_analysis_results"))
        connection.execute(text("DROP TABLE IF EXISTS segment_summary"))
        connection.commit()

    rfm.to_sql("rfm_analysis_results", engine, if_exists="replace", index=False)
    segment_summary.reset_index().to_sql("segment_summary", engine, if_exists="replace", index=False)

    if verbose:
        print("✓ rfm_analysis_results and segment_summary written to Postgres")


if __name__ == "__main__":
    from db import get_engine

    engine = get_engine()
    rfm, segment_summary = run_rfm(engine)
    rfm.to_csv("outputs/rfm_analysis_results.csv", index=False)
    segment_summary.to_csv("outputs/segment_summary.csv")
    write_rfm_to_db(engine, rfm, segment_summary)
    print("\n✓ Exported to outputs/rfm_analysis_results.csv and outputs/segment_summary.csv")
