import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


def load_churn_source_data(engine):
    customers = pd.read_sql("SELECT customer_id, customer_unique_id, customer_state FROM customers", engine)
    orders = pd.read_sql(
        "SELECT order_id, customer_id, order_status, order_purchase_timestamp, "
        "order_delivered_customer_date, order_estimated_delivery_date FROM orders",
        engine,
    )
    order_items = pd.read_sql("SELECT order_id, price, freight_value FROM order_items", engine)
    payments = pd.read_sql("SELECT order_id, payment_type, payment_installments, payment_value FROM payments", engine)
    reviews = pd.read_sql("SELECT order_id, review_score FROM reviews", engine)
    return customers, orders, order_items, payments, reviews


def build_order_level_features(orders, order_items, payments, reviews):
    """
    Aggregates order_items and payments to ONE ROW PER ORDER independently
    BEFORE merging them together. The original script merged both onto
    orders via separate order_id joins, causing a many-to-many fan-out for
    any order with multiple items AND a split/installment payment — e.g. a
    2-item order paid in 2 installments produced 4 duplicated rows, each
    contributing its item's price to the sum, inflating monetary_value.
    """
    order_items = order_items.copy()
    order_items["price"] = pd.to_numeric(order_items["price"], errors="coerce")
    order_items["freight_value"] = pd.to_numeric(order_items["freight_value"], errors="coerce")
    order_items["total_value"] = order_items["price"] + order_items["freight_value"]
    items_agg = order_items.groupby("order_id")["total_value"].sum().reset_index()

    payments_agg = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        avg_installments=("payment_installments", "mean"),
    ).reset_index()

    reviews_agg = reviews.groupby("order_id")["review_score"].mean().reset_index()

    orders = orders.copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])
    orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"])
    orders["delivery_delay_days"] = (
        orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]
    ).dt.days.fillna(0)

    order_level = (
        orders.merge(items_agg, on="order_id", how="inner")  # drops the 775 item-less orders
        .merge(payments_agg, on="order_id", how="left")
        .merge(reviews_agg, on="order_id", how="left")
    )

    return order_level


def build_customer_features(order_level, customers):
    """Groups by customer_unique_id — the true customer identity — not customer_id."""
    order_level = order_level.merge(
        customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left"
    )

    reference_date = order_level["order_purchase_timestamp"].max()

    customer_features = order_level.groupby("customer_unique_id").agg(
        recency_days=("order_purchase_timestamp", lambda x: (reference_date - x.max()).days),
        frequency=("order_id", "nunique"),  # now a real distinct-order count per customer
        monetary_value=("total_value", "sum"),
        avg_review_score=("review_score", "mean"),
        avg_payment_value=("payment_value", "mean"),
        avg_installments=("avg_installments", "mean"),
        avg_delivery_delay=("delivery_delay_days", "mean"),
    ).reset_index()

    # Churn label: no purchase in the last 180 days relative to dataset's own max date.
    # CAVEAT: ~97% of customers in this dataset only ever place one order, so this label
    # mostly reflects "how long ago was this customer's single order" rather than genuine
    # repeat-purchase attrition. Frequency will be highly skewed toward 1 — expected, not a bug.
    customer_features["churn"] = (customer_features["recency_days"] > 180).astype(int)

    return customer_features, reference_date


def run_churn_features(engine, verbose=True):
    customers, orders, order_items, payments, reviews = load_churn_source_data(engine)
    order_level = build_order_level_features(orders, order_items, payments, reviews)
    customer_features, reference_date = build_customer_features(order_level, customers)

    if verbose:
        print("=" * 80)
        print("CHURN FEATURE ENGINEERING")
        print("=" * 80)
        print(f"Reference date: {reference_date.date()}")
        print(f"Customers (customer_unique_id): {len(customer_features):,}")
        print(f"Max frequency observed: {customer_features['frequency'].max()} (sanity check)")
        print(f"Frequency distribution:\n{customer_features['frequency'].value_counts().sort_index()}")
        print(f"\nChurn distribution:\n{customer_features['churn'].value_counts()}")
        print(f"Churn rate: {customer_features['churn'].mean()*100:.1f}%")
        print("=" * 80)

    return customer_features


if __name__ == "__main__":
    from db import get_engine

    features = run_churn_features(get_engine())
    features.to_csv("outputs/customer_churn_features.csv", index=False)
    print("\n✓ Exported to outputs/customer_churn_features.csv")
