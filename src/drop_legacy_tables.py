from sqlalchemy import text
from db import get_engine

LEGACY_TABLES = [
    "olist_customers_dataset",
    "olist_geolocation_dataset",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "olist_orders_dataset",
    "olist_products_dataset",
    "olist_sellers_dataset",
    "customer_churn_analysis",
    "customer_churn_prediction",
]

if __name__ == "__main__":
    engine = get_engine()
    with engine.connect() as conn:
        for table in LEGACY_TABLES:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            print(f"Dropped {table}")
        conn.commit()
    print("Cleanup done.")
