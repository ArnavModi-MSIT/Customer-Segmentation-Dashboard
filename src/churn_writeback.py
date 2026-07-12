import pandas as pd
from sqlalchemy import text
from datetime import datetime


def write_churn_predictions(engine, predictions_path="outputs/customer_churn_predictions.csv",
                             table_name="customer_churn_predictions", verbose=True):
    df = pd.read_csv(predictions_path)
    df["churn_probability"] = df["churn_probability"].round(4)

    with engine.connect() as connection:
        connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        connection.commit()

    df.to_sql(table_name, engine, if_exists="replace", index=False)

    with engine.connect() as connection:
        count = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        segments = connection.execute(
            text(f"SELECT churn_risk, COUNT(*) FROM {table_name} GROUP BY churn_risk ORDER BY churn_risk")
        ).fetchall()
        connection.commit()

    if verbose:
        print("=" * 80)
        print("WRITING CHURN PREDICTIONS TO POSTGRESQL")
        print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"✓ Table: {table_name}")
        print(f"✓ Records: {count:,}")
        print("✓ Risk Distribution:")
        for segment, cnt in segments:
            pct = (cnt / count) * 100
            print(f"  {segment}: {cnt:,} ({pct:.1f}%)")
        print(f"\n✅ Ready to connect Power BI to '{table_name}' table")
        print("=" * 80)

    return {"table": table_name, "record_count": count, "risk_distribution": dict(segments)}


if __name__ == "__main__":
    from db import get_engine

    write_churn_predictions(get_engine())
