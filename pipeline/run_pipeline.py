"""
run_pipeline.py
---------------
Master script — runs the full data pipeline in one command.

Usage (from inside the pipeline/ folder):
    python run_pipeline.py

What it does:
    1. Ingest  — loads and validates the raw CSV
    2. Transform — classifies pages, builds session funnel
    3. Load     — saves both tables into SQLite
    4. Export   — saves processed CSVs to data/processed/
"""

import sys
import os
import pandas as pd

# So Python can find our sibling files
sys.path.append(os.path.dirname(__file__))

from ingest    import load_raw_data
from transform import transform
from load_sql  import load_to_sqlite


# ── File paths ───────────────────────────────────────────────────────────────
RAW_CSV        = r"C:\Users\dell\Desktop\Customer-Behaviour-Analytics\data\raw.csv"
DB_PATH        = "../Customer-Behaviour-Analytics/database/ecommerce.db"
PROCESSED_DIR  = "../Customer-Behaviour-Analytics/data/processed/"


def run():
    print("=" * 50)
    print("  CONVERSION INTELLIGENCE — DATA PIPELINE")
    print("=" * 50)
    print()

    # ── Step 1: Ingest ───────────────────────────────
    raw = load_raw_data(r"C:\Users\dell\Desktop\Customer-Behaviour-Analytics\data\raw.csv")

    # ── Step 2: Transform ────────────────────────────
    raw_events, session_funnel = transform(raw)

    # ── Step 3: Load into SQLite ─────────────────────
    load_to_sqlite(raw_events, session_funnel, db_path=DB_PATH)

    # ── Step 4: Also save as CSV ─────────────────────
    # Useful for Power BI, Excel checks, or quick lookups
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    raw_out      = os.path.join(PROCESSED_DIR, "raw_events_clean.csv")
    sessions_out = os.path.join(PROCESSED_DIR, "session_funnel.csv")

    raw_events.to_csv(raw_out,      index=False)
    session_funnel.to_csv(sessions_out, index=False)

    print(f"  CSVs saved:")
    print(f"    {raw_out}")
    print(f"    {sessions_out}")

    print()
    print("=" * 50)
    print("  PIPELINE COMPLETE — database is ready")
    print("=" * 50)


if __name__ == "__main__":
    run()