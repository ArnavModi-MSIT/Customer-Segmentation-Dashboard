"""
Runs the full pipeline end to end:
  ingestion -> eda -> rfm -> churn_features -> churn_model -> churn_writeback -> business_insights

Each stage's output feeds the next. Run stages individually during development
(python src/eda.py, etc.); use this for a full clean run or for CI.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from db import get_engine
from ingestion import run_ingestion
from eda import run_eda
from rfm import run_rfm, write_rfm_to_db
from churn_features import run_churn_features
from churn_model import run_churn_model
from churn_writeback import write_churn_predictions
from business_insights import run_business_insights

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def main(verbose=True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()

    print("\n" + "#" * 80)
    print("# STAGE 1/6: INGESTION")
    print("#" * 80)
    run_ingestion(engine, verbose=verbose)

    print("\n" + "#" * 80)
    print("# STAGE 2/6: EDA")
    print("#" * 80)
    run_eda(engine, verbose=verbose)

    print("\n" + "#" * 80)
    print("# STAGE 3/6: RFM SEGMENTATION")
    print("#" * 80)
    rfm, segment_summary = run_rfm(engine, verbose=verbose)
    rfm.to_csv(os.path.join(OUTPUT_DIR, "rfm_analysis_results.csv"), index=False)
    segment_summary.to_csv(os.path.join(OUTPUT_DIR, "segment_summary.csv"))
    write_rfm_to_db(engine, rfm, segment_summary, verbose=verbose)

    print("\n" + "#" * 80)
    print("# STAGE 4/6: CHURN FEATURE ENGINEERING")
    print("#" * 80)
    features = run_churn_features(engine, verbose=verbose)
    features_path = os.path.join(OUTPUT_DIR, "customer_churn_features.csv")
    features.to_csv(features_path, index=False)

    print("\n" + "#" * 80)
    print("# STAGE 5/6: CHURN MODEL")
    print("#" * 80)
    predictions, metrics, feature_importance = run_churn_model(features, verbose=verbose)
    predictions_path = os.path.join(OUTPUT_DIR, "customer_churn_predictions.csv")
    predictions.to_csv(predictions_path, index=False)
    write_churn_predictions(engine, predictions_path=predictions_path, verbose=verbose)

    print("\n" + "#" * 80)
    print("# STAGE 6/6: BUSINESS INSIGHTS & ROI")
    print("#" * 80)
    run_business_insights(verbose=verbose, features_path=features_path, predictions_path=predictions_path)

    print("\n" + "#" * 80)
    print("# PIPELINE COMPLETE")
    print("#" * 80)
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Outputs written to: {OUTPUT_DIR}")
    print("Tables in Postgres: customers, orders, order_items, payments, reviews, sellers,")
    print("  geolocation, products, product_category_name_translation,")
    print("  rfm_analysis_results, segment_summary, customer_churn_predictions")


if __name__ == "__main__":
    main()
