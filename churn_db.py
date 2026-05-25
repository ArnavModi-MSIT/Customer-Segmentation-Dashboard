import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

username = "postgres"
password = "root"
host = "localhost"
port = "5432"
database = "olist_project"

engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")

print("="*80)
print("LOADING CHURN PREDICTIONS TO POSTGRESQL")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

try:
    df = pd.read_csv('customer_churn_predictions.csv')
    print(f"✓ CSV loaded: {len(df)} records")
except Exception as e:
    print(f"❌ Error loading CSV: {str(e)}")
    exit()

df['churn_probability'] = df['churn_probability'].round(4)

try:
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS customer_churn_analysis"))
        connection.commit()
    
    df.to_sql('customer_churn_analysis', engine, if_exists='replace', index=False)
    print(f"✓ Table created: customer_churn_analysis")
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM customer_churn_analysis"))
        count = result.scalar()
        print(f"✓ Records inserted: {count:,}\n")
        
        result = connection.execute(text("SELECT churn_risk, COUNT(*) FROM customer_churn_analysis GROUP BY churn_risk ORDER BY churn_risk"))
        segments = result.fetchall()
        print(f"✓ Risk Distribution:")
        for segment, cnt in segments:
            pct = (cnt / count) * 100
            print(f"  {segment}: {cnt:,} ({pct:.1f}%)")
        
        connection.commit()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit()

print(f"\nEnd: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print("✅ Ready to connect Power BI to customer_churn_analysis table")
print("="*80)