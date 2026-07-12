import os
import sys
import pandas as pd
from sqlalchemy import text
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR

RAW_FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
}

PRODUCTS_FILE = "olist_products_dataset.csv"
TRANSLATION_FILE = "product_category_name_translation.csv"


def load_products_with_translation():
    """
    Cleans and enriches the products table:
      - 610 rows with missing category/name/description metadata are KEPT
        (not dropped) and tagged category='unknown' — dropping them would
        silently orphan any order_items referencing those product_ids.
      - Joins product_category_name_translation for English category names,
        used downstream in EDA/RFM/Power BI instead of Portuguese labels.
    """
    products = pd.read_csv(os.path.join(DATA_DIR, PRODUCTS_FILE), low_memory=False)
    translation = pd.read_csv(os.path.join(DATA_DIR, TRANSLATION_FILE))

    products["product_category_name"] = products["product_category_name"].fillna("unknown")

    products = products.merge(translation, on="product_category_name", how="left")
    products["product_category_name_english"] = products["product_category_name_english"].fillna(
        products["product_category_name"]
    )

    return products


def load_raw_tables(engine, verbose=True):
    stats = {"successful": [], "failed": [], "total_rows": 0}

    for fname, table_name in RAW_FILES.items():
        path = os.path.join(DATA_DIR, fname)
        try:
            df = pd.read_csv(path, low_memory=False)
            df.to_sql(table_name, engine, if_exists="replace", index=False, chunksize=5000)
            stats["successful"].append(table_name)
            stats["total_rows"] += len(df)
            if verbose:
                print(f"✓ {table_name}: {len(df):,} rows")
        except Exception as e:
            stats["failed"].append((table_name, str(e)))
            if verbose:
                print(f"❌ {table_name}: {e}")

    # products loaded separately due to cleanup + translation join
    try:
        products = load_products_with_translation()
        products.to_sql("products", engine, if_exists="replace", index=False, chunksize=5000)
        stats["successful"].append("products")
        stats["total_rows"] += len(products)
        if verbose:
            print(f"✓ products: {len(products):,} rows (cleaned + English category names)")
    except Exception as e:
        stats["failed"].append(("products", str(e)))
        if verbose:
            print(f"❌ products: {e}")

    return stats


def verify_tables(engine, verbose=True):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        )
        tables = [row[0] for row in result.fetchall()]

        report = {}
        for table_name in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            report[table_name] = count
            if verbose:
                print(f"  {table_name:20} {count:>8,} rows")

    return report


def run_ingestion(engine, verbose=True):
    if verbose:
        print("=" * 80)
        print("INGESTION")
        print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    stats = load_raw_tables(engine, verbose=verbose)

    if verbose:
        print("\nVerifying tables in DB:")
        verify_tables(engine, verbose=verbose)
        print("=" * 80)
        print(f"✅ Ingestion complete — {stats['total_rows']:,} total rows across {len(stats['successful'])} tables")
        if stats["failed"]:
            print(f"⚠ Failed: {stats['failed']}")
        print("=" * 80)

    return stats


if __name__ == "__main__":
    from db import get_engine

    run_ingestion(get_engine())
