"""
ingest.py
---------
Step 1 of the pipeline.
Reads the raw CSV, does basic validation, and returns a clean DataFrame.
"""

import pandas as pd
import os


# Columns we expect in the raw file
REQUIRED_COLUMNS = [
    'fullVisitorId', 'visitId', 'visitStartTime',
    'pageviews', 'transactions', 'device_type',
    'source', 'page', 'hit_type', 'hit_time'
]


def load_raw_data(filepath):
    """
    Loads the raw CSV file and validates it.
    Returns a pandas DataFrame.
    """

    # Check file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found: {filepath}")

    print(f"Loading raw data from: {filepath}")
    df = pd.read_csv(filepath)

    print(f"  Rows loaded     : {len(df)}")
    print(f"  Columns found   : {list(df.columns)}")

    # Check all required columns are present
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in raw file: {missing}")

    # ----- Basic Cleaning -----

    # 1. Drop rows where page or device_type is missing (critical fields)
    before = len(df)
    df = df.dropna(subset=['page', 'device_type'])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  Dropped {dropped} rows with missing page/device_type")

    # 2. Fill missing transactions with 0
    #    NaN in transactions means no purchase happened in that row
    df['transactions'] = df['transactions'].fillna(0)

    # 3. Create session_id by combining fullVisitorId and visitId
    #    This uniquely identifies each user visit/session
    df['session_id'] = df['fullVisitorId'].astype(str) + '_' + df['visitId'].astype(str)

    print(f"  Unique sessions : {df['session_id'].nunique()}")
    print(f"  Ingest complete.\n")

    return df


# Quick test — run this file directly to verify
if __name__ == "__main__":
    df = load_raw_data(r"C:\Users\dell\Desktop\Customer-Behaviour-Analytics\ecommerce-user-behaviour-raw.csv")
    print(df.head(3))