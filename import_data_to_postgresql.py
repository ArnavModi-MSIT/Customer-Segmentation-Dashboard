import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# PostgreSQL connection (configurable via environment variables)
# Set DB credentials in environment for safety: DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
username = os.getenv('DB_USER', 'postgres')
password = os.getenv('DB_PASS', 'root')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
database = os.getenv('DB_NAME', 'olist_project')

# Create connection string
connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# CSV files and target table names (no duplicates)
files = {
    "olist_customers_dataset.csv": "olist_customers_dataset",
    "olist_orders_dataset.csv": "olist_orders_dataset",
    "olist_order_items_dataset.csv": "olist_order_items_dataset",
    "olist_order_payments_dataset.csv": "olist_order_payments_dataset",
    "olist_order_reviews_dataset.csv": "olist_order_reviews_dataset",
    "olist_products_dataset.csv": "olist_products_dataset",
    "olist_geolocation_dataset.csv": "olist_geolocation_dataset",
    "olist_sellers_dataset.csv": "olist_sellers_dataset"
}

print("="*60)
print("OLIST DATA IMPORT SCRIPT")
print("="*60)
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Database: {database}")
print("="*60)

# Track statistics
import_stats = {
    "successful": [],
    "failed": [],
    "total_rows": 0
}

# Load all tables
for file_name, table_name in files.items():
    try:
        path = os.path.join(os.path.dirname(__file__), "data", file_name)
        
        # Check if file exists
        if not os.path.exists(path):
            print(f"❌ ERROR: File not found - {path}")
            import_stats["failed"].append(table_name)
            continue
        
        # Read CSV with error handling
        print(f"\n📥 Importing {table_name}...", end=" ")
        # Read CSV with explicit params to avoid dtype inference issues
        df = pd.read_csv(path, encoding='utf-8', low_memory=False)
        
        # Get row and column count
        rows = len(df)
        cols = len(df.columns)
        import_stats["total_rows"] += rows
        
        # Import to PostgreSQL
        df.to_sql(
            table_name,
            engine,
            if_exists="replace",  # Replace existing table
            index=False,
            chunksize=5000  # Import in chunks for large files
        )
        
        print(f"✅ SUCCESS")
        print(f"   └─ Rows: {rows:,} | Columns: {cols}")
        import_stats["successful"].append(table_name)
        
    except FileNotFoundError:
        print(f"❌ ERROR: File not found - {path}")
        import_stats["failed"].append(table_name)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import_stats["failed"].append(table_name)

print("\n" + "="*60)
print("IMPORT SUMMARY")
print("="*60)
print(f"✅ Successful: {len(import_stats['successful'])} tables")
for table in import_stats['successful']:
    print(f"   ✓ {table}")

if import_stats['failed']:
    print(f"\n❌ Failed: {len(import_stats['failed'])} tables")
    for table in import_stats['failed']:
        print(f"   ✗ {table}")

print(f"\n📊 Total Rows Imported: {import_stats['total_rows']:,}")
print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Verify tables in database
print("\n🔍 VERIFYING TABLES IN DATABASE...")
print("="*60)

try:
    with engine.connect() as connection:
        # Get all tables
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name
        """)
        result = connection.execute(query)
        tables = result.fetchall()
        
        print(f"\nTotal Tables in Database: {len(tables)}")
        for table in tables:
            table_name = table[0]
            # Get row count
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            count_result = connection.execute(count_query)
            row_count = count_result.scalar()
            print(f"  ✓ {table_name:40} - {row_count:,} rows")
        
        connection.commit()
        
except Exception as e:
    print(f"❌ Error verifying tables: {str(e)}")

print("="*60)
print("✅ DATA IMPORT COMPLETE!")
print("="*60)