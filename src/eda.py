import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


def load_tables(engine):
    tables = {
        "customers": "customers",
        "orders": "orders",
        "order_items": "order_items",
        "products": "products",
        "reviews": "reviews",
        "sellers": "sellers",
        "payments": "payments",
    }
    dfs = {name: pd.read_sql(f"SELECT * FROM {table}", engine) for name, table in tables.items()}
    return dfs


def check_missing_values(df, name):
    missing = df.isnull().sum()
    report = {}
    for col in missing[missing > 0].index:
        pct = (missing[col] / len(df)) * 100
        report[col] = {"missing": int(missing[col]), "pct": round(pct, 2)}
    return report


def compute_revenue_metrics(orders_df, order_items_df, customers_df):
    """
    NOTE: order value stats are computed on ORDER-level totals, not on
    order_item rows. A prior version averaged over order_items directly,
    which understates order value for multi-item orders (each item row
    was treated as a separate "order").
    """
    order_items_df = order_items_df.copy()
    order_items_df["price"] = pd.to_numeric(order_items_df["price"], errors="coerce")
    order_items_df["freight_value"] = pd.to_numeric(order_items_df["freight_value"], errors="coerce")
    order_items_df["total_value"] = order_items_df["price"] + order_items_df["freight_value"]

    # Aggregate to one row per order BEFORE computing avg/median/min/max
    order_totals = order_items_df.groupby("order_id")["total_value"].sum().reset_index()

    orders_full = orders_df.merge(order_totals, on="order_id", how="inner")
    orders_full = orders_full.merge(customers_df, on="customer_id", how="inner")

    delivered = orders_full[orders_full["order_status"] == "delivered"]

    return {
        "total_revenue": delivered["total_value"].sum(),
        "avg_order_value": delivered["total_value"].mean(),
        "median_order_value": delivered["total_value"].median(),
        "min_order_value": delivered["total_value"].min(),
        "max_order_value": delivered["total_value"].max(),
        "orders_full": orders_full,
    }


def compute_order_metrics(orders_df, order_items_df):
    total_orders = len(orders_df)
    delivered_orders = len(orders_df[orders_df["order_status"] == "delivered"])
    canceled_orders = len(orders_df[orders_df["order_status"] == "canceled"])
    return {
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "delivered_pct": round((delivered_orders / total_orders) * 100, 1),
        "canceled_orders": canceled_orders,
        "avg_items_per_order": round(len(order_items_df) / total_orders, 2),
    }


def compute_customer_metrics(customers_df, orders_df):
    """
    Olist's customer_id is a per-order surrogate key — every order gets a
    unique customer_id, so grouping by it makes every customer look like a
    one-time buyer. customer_unique_id is the actual persistent customer
    identity and must be used for repeat-purchase / frequency metrics.
    """
    orders_with_identity = orders_df.merge(
        customers_df[["customer_id", "customer_unique_id"]], on="customer_id", how="left"
    )

    repeat_customers = orders_with_identity.groupby("customer_unique_id").size()
    repeat_rate = (len(repeat_customers[repeat_customers > 1]) / customers_df["customer_unique_id"].nunique()) * 100

    return {
        "unique_customers": customers_df["customer_unique_id"].nunique(),
        "unique_states": customers_df["customer_state"].nunique(),
        "unique_cities": customers_df["customer_city"].nunique(),
        "repeat_purchase_rate_pct": round(repeat_rate, 2),
        "avg_orders_per_customer": round(len(orders_df) / customers_df["customer_unique_id"].nunique(), 2),
    }


def compute_review_metrics(reviews_df):
    reviews_df = reviews_df.copy()
    reviews_df["review_score"] = pd.to_numeric(reviews_df["review_score"], errors="coerce")
    return {
        "total_reviews": len(reviews_df),
        "avg_rating": round(reviews_df["review_score"].mean(), 2),
        "median_rating": round(reviews_df["review_score"].median(), 2),
        "std_rating": round(reviews_df["review_score"].std(), 2),
        "rating_distribution": reviews_df["review_score"].value_counts().sort_index().to_dict(),
    }


def compute_category_metrics(order_items_df, products_df, top_n=10):
    order_items_df = order_items_df.copy()
    order_items_df["price"] = pd.to_numeric(order_items_df["price"], errors="coerce")

    merged = order_items_df.merge(
        products_df[["product_id", "product_category_name_english"]], on="product_id", how="left"
    )
    merged["product_category_name_english"] = merged["product_category_name_english"].fillna("unknown")

    top_categories = (
        merged.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )
    return top_categories.round(2).to_dict()


def data_quality_checks(customers_df, orders_df, order_items_df, reviews_df):
    orders_without_items = orders_df["order_id"].nunique() - order_items_df["order_id"].nunique()
    return {
        "no_duplicate_customer_ids": customers_df["customer_id"].duplicated().sum() == 0,
        "no_duplicate_order_ids": orders_df["order_id"].duplicated().sum() == 0,
        "prices_positive": bool((order_items_df["price"] > 0).all()),
        "freight_non_negative": bool((order_items_df["freight_value"] >= 0).all()),
        "valid_review_scores": bool(reviews_df["review_score"].between(1, 5).all()),
        "orders_without_items": int(orders_without_items),
    }


def run_eda(engine, verbose=True):
    dfs = load_tables(engine)

    missing_report = {name: check_missing_values(df, name) for name, df in dfs.items()}
    revenue = compute_revenue_metrics(dfs["orders"], dfs["order_items"], dfs["customers"])
    order_metrics = compute_order_metrics(dfs["orders"], dfs["order_items"])
    customer_metrics = compute_customer_metrics(dfs["customers"], dfs["orders"])
    review_metrics = compute_review_metrics(dfs["reviews"])
    category_metrics = compute_category_metrics(dfs["order_items"], dfs["products"])
    quality = data_quality_checks(dfs["customers"], dfs["orders"], dfs["order_items"], dfs["reviews"])

    summary = {
        "generated_at": datetime.now().isoformat(),
        "missing_values": missing_report,
        "revenue": {k: v for k, v in revenue.items() if k != "orders_full"},
        "orders": order_metrics,
        "customers": customer_metrics,
        "reviews": review_metrics,
        "top_categories_by_revenue": category_metrics,
        "data_quality": quality,
    }

    if verbose:
        print("=" * 80)
        print("EDA SUMMARY")
        print("=" * 80)
        print(f"Total Revenue: R$ {revenue['total_revenue']:,.2f}")
        print(f"Avg Order Value (per order, corrected): R$ {revenue['avg_order_value']:,.2f}")
        print(f"Median Order Value: R$ {revenue['median_order_value']:,.2f}")
        print(f"Total Orders: {order_metrics['total_orders']:,} | Delivered: {order_metrics['delivered_pct']}%")
        print(f"Unique Customers: {customer_metrics['unique_customers']:,}")
        print(f"Repeat Purchase Rate: {customer_metrics['repeat_purchase_rate_pct']}%")
        print(f"Avg Rating: {review_metrics['avg_rating']}/5.0")
        print(f"Orders without items (excluded from revenue): {quality['orders_without_items']}")
        print("Top 5 Categories by Revenue:")
        for cat, rev in list(category_metrics.items())[:5]:
            print(f"  {cat}: R$ {rev:,.2f}")
        print("Data Quality:", quality)
        print("=" * 80)

    return summary


if __name__ == "__main__":
    from db import get_engine

    run_eda(get_engine())