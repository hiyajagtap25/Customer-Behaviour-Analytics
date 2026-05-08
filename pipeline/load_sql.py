
import sqlite3
import pandas as pd
import os


DB_PATH = "../database/ecommerce.db"

#saves both df in sqlite
def load_to_sqlite(raw_events, session_funnel, db_path=DB_PATH):
    

    # Make sure the database folder exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print(f"Loading data into SQLite: {db_path}")

    # Open a connection to the database file
    # (SQLite creates the file automatically if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # ── Table 1: raw_events ──────────────────────────────────────────────────
    # Select only the columns we actually need for analysis
    raw_cols = [
        'session_id', 'fullVisitorId', 'visitId', 'visitStartTime',
        'device_type', 'source', 'source_group',
        'page', 'page_cat', 'hit_type', 'transactions'
    ]

    raw_to_save = raw_events[raw_cols].copy()

    # fullVisitorId is uint64 which is too large for SQLite INTEGER — save as text
    raw_to_save['fullVisitorId'] = raw_to_save['fullVisitorId'].astype(str)

    # if_exists='replace' → drops and recreates the table on every pipeline run
    # This keeps the database in sync with your latest CSV file
    raw_to_save.to_sql(
        name      = 'raw_events',
        con       = conn,
        if_exists = 'replace',
        index     = False
    )
    print(f"  raw_events      : {len(raw_to_save)} rows loaded")

    # ── Table 2: session_funnel ──────────────────────────────────────────────
    session_funnel.to_sql(
        name      = 'session_funnel',
        con       = conn,
        if_exists = 'replace',
        index     = False
    )
    print(f"  session_funnel  : {len(session_funnel)} rows loaded")

    # ── Quick verification ───────────────────────────────────────────────────
    # Read back row counts to confirm the data landed correctly
    raw_check     = pd.read_sql("SELECT COUNT(*) AS cnt FROM raw_events",     conn).iloc[0, 0]
    session_check = pd.read_sql("SELECT COUNT(*) AS cnt FROM session_funnel", conn).iloc[0, 0]

    print(f"\n  Verification — rows in DB:")
    print(f"    raw_events     : {raw_check}")
    print(f"    session_funnel : {session_check}")

    conn.close()
    print(f"\n  Database saved at: {os.path.abspath(db_path)}")
    print(f"  Load complete.\n")


# Quick test — run this file directly to check
if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from ingest import load_raw_data
    from transform import transform

    raw = load_raw_data(r"C:\Users\dell\Desktop\Customer-Behaviour-Analytics\data\raw.csv")
    raw_events, session_funnel = transform(raw)
    load_to_sqlite(raw_events, session_funnel)