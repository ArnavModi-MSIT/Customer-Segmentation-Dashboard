"""
Runs the full pipeline end to end:
  prepare_data -> eda -> rfm -> business_insights -> export_to_excel

No database, no ML — pure pandas analytics, ending in one Excel workbook
(data/processed/olist_analytics.xlsx) that Power BI reads directly.

Each stage can also be run independently, e.g. `python src/eda.py`.
"""
import os
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from prepare_data import run_prepare_data
from eda import run_eda
from rfm import run_rfm
from business_insights import run_business_insights
from export_to_excel import export_to_excel

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def main(verbose=True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n" + "#" * 80)
    print("# STAGE 1/4: PREPARE DATA")
    print("#" * 80)
    tables = run_prepare_data(verbose=verbose)

    print("\n" + "#" * 80)
    print("# STAGE 2/4: EDA")
    print("#" * 80)
    run_eda(tables, verbose=verbose)

    print("\n" + "#" * 80)
    print("# STAGE 3/4: RFM SEGMENTATION")
    print("#" * 80)
    rfm, segment_summary = run_rfm(tables["fact_orders"], verbose=verbose)
    rfm.to_csv(os.path.join(OUTPUT_DIR, "rfm_analysis_results.csv"), index=False)
    segment_summary.to_csv(os.path.join(OUTPUT_DIR, "segment_summary.csv"), index=False)

    tables["rfm_customer_segments"] = rfm
    tables["segment_summary"] = segment_summary

    print("\n" + "#" * 80)
    print("# STAGE 4/4: BUSINESS INSIGHTS & EXCEL EXPORT")
    print("#" * 80)
    run_business_insights(rfm, segment_summary, verbose=verbose)
    export_to_excel(tables, verbose=verbose)

    print("\n" + "#" * 80)
    print("# PIPELINE COMPLETE")
    print("#" * 80)
    print(f"CSV outputs: {OUTPUT_DIR}")
    print("Excel workbook (Power BI source): data/processed/olist_analytics.xlsx")


if __name__ == "__main__":
    main()
