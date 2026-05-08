import sqlite3
import pandas as pd
import os

# Path to the database — adjust if running from a different folder
DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")


def get_connection():
    """Opens and returns a SQLite connection."""
    return sqlite3.connect(DB_PATH)


# ══════════════════════════════════════════════════════════════
# SECTION 1 — FUNNEL QUERIES
# ══════════════════════════════════════════════════════════════

def get_funnel_summary():
    """
    Returns how many sessions reached each funnel stage.
    Used for: the main funnel bar chart on the dashboard.

    Output columns: drop_off, funnel_stage, sessions, pct_of_total
    """
    query = """
        SELECT
            drop_off,
            funnel_stage,
            COUNT(*) AS sessions,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
        FROM session_funnel
        GROUP BY drop_off, funnel_stage
        ORDER BY funnel_stage
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_conversion_rate():
    """
    Returns overall conversion KPIs in a single row.
    Used for: the 3 KPI cards at the top of the dashboard.

    Output columns: total_sessions, total_conversions, conversion_rate_pct
    """
    query = """
        SELECT
            COUNT(*)                                     AS total_sessions,
            SUM(converted)                               AS total_conversions,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 2) AS conversion_rate_pct
        FROM session_funnel
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_stepwise_dropoff():
    """
    Returns how many users dropped between each funnel step.
    Used for: showing percentage drop between stages.

    Output columns: funnel_stage, last_step, sessions_reached
    """
    query = """
        SELECT
            funnel_stage,
            last_step,
            COUNT(*) AS sessions_reached
        FROM session_funnel
        GROUP BY funnel_stage, last_step
        ORDER BY funnel_stage
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    # Calculate drop % between steps using pandas (simpler than SQL window functions)
    df['drop_from_prev_pct'] = (
        df['sessions_reached']
        .pct_change()               # gives change as decimal, e.g. -0.55
        .mul(-100)                  # flip sign and convert to percentage
        .round(1)
        .fillna(0)
    )
    return df


# ══════════════════════════════════════════════════════════════
# SECTION 2 — DEVICE QUERIES
# ══════════════════════════════════════════════════════════════

def get_device_breakdown():
    """
    Returns funnel performance split by device type.
    Used for: device comparison bar chart.

    Output columns: device_type, total_sessions, bounced,
                    dropped_at_product, dropped_at_cart,
                    reached_checkout, conversions, conv_rate_pct
    """
    query = """
        SELECT
            device_type,
            COUNT(*)                                                        AS total_sessions,
            SUM(CASE WHEN funnel_stage = 1 THEN 1 ELSE 0 END)              AS bounced,
            SUM(CASE WHEN funnel_stage = 2 THEN 1 ELSE 0 END)              AS dropped_at_product,
            SUM(CASE WHEN funnel_stage = 3 THEN 1 ELSE 0 END)              AS dropped_at_cart,
            SUM(CASE WHEN funnel_stage = 4 THEN 1 ELSE 0 END)              AS reached_checkout,
            SUM(converted)                                                  AS conversions,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 2)                    AS conv_rate_pct
        FROM session_funnel
        GROUP BY device_type
        ORDER BY total_sessions DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_device_share():
    """
    Returns what % of total traffic each device type contributes.
    Used for: device donut/pie chart.

    Output columns: device_type, sessions, share_pct
    """
    query = """
        SELECT
            device_type,
            COUNT(*) AS sessions,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS share_pct
        FROM session_funnel
        GROUP BY device_type
        ORDER BY sessions DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ══════════════════════════════════════════════════════════════
# SECTION 3 — TRAFFIC SOURCE QUERIES
# ══════════════════════════════════════════════════════════════

def get_source_performance():
    """
    Returns conversion performance by traffic source group.
    Used for: source comparison bar chart.

    Output columns: source_group, total_sessions, conversions,
                    conv_rate_pct, avg_funnel_depth
    """
    query = """
        SELECT
            source_group,
            COUNT(*)                                            AS total_sessions,
            SUM(converted)                                      AS conversions,
            ROUND(SUM(converted) * 100.0 / COUNT(*), 2)        AS conv_rate_pct,
            ROUND(AVG(funnel_stage), 2)                         AS avg_funnel_depth
        FROM session_funnel
        GROUP BY source_group
        ORDER BY total_sessions DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_bounce_by_source():
    """
    Returns bounce rate for each traffic source.
    Used for: identifying which source brings low-quality traffic.

    Output columns: source_group, total_sessions, bounces, bounce_rate_pct
    """
    query = """
        SELECT
            source_group,
            COUNT(*)                                                    AS total_sessions,
            SUM(CASE WHEN funnel_stage = 1 THEN 1 ELSE 0 END)          AS bounces,
            ROUND(
                SUM(CASE WHEN funnel_stage = 1 THEN 1 ELSE 0 END)
                * 100.0 / COUNT(*), 1
            )                                                           AS bounce_rate_pct
        FROM session_funnel
        GROUP BY source_group
        ORDER BY bounce_rate_pct DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ══════════════════════════════════════════════════════════════
# SECTION 4 — PAGE QUERIES  (uses raw_events table)
# ══════════════════════════════════════════════════════════════

def get_top_pages(limit=15):
    """
    Returns the most visited pages.
    Used for: top pages table on dashboard.

    Output columns: page, page_cat, hits
    """
    query = f"""
        SELECT
            page,
            page_cat,
            COUNT(*) AS hits
        FROM raw_events
        GROUP BY page, page_cat
        ORDER BY hits DESC
        LIMIT {limit}
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_stage_reach():
    """
    Returns how many unique sessions hit each funnel stage page.
    Used for: funnel reach numbers.

    Output columns: page_cat, unique_sessions, total_hits
    """
    query = """
        SELECT
            page_cat,
            COUNT(DISTINCT session_id) AS unique_sessions,
            COUNT(*)                   AS total_hits
        FROM raw_events
        WHERE page_cat != 'other'
        GROUP BY page_cat
        ORDER BY unique_sessions DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ══════════════════════════════════════════════════════════════
# SECTION 5 — CONVERSION QUERIES
# ══════════════════════════════════════════════════════════════

def get_converter_profile():
    """
    Returns device + source breakdown of sessions that actually converted.
    Used for: AI insight generation and converter profile card.

    Output columns: device_type, source_group, converted_sessions
    """
    query = """
        SELECT
            device_type,
            source_group,
            COUNT(*) AS converted_sessions
        FROM session_funnel
        WHERE converted = 1
        GROUP BY device_type, source_group
        ORDER BY converted_sessions DESC
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ══════════════════════════════════════════════════════════════
# QUICK TEST — run this file directly to check all queries
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("\n── Funnel Summary ──────────────────────────────")
    print(get_funnel_summary().to_string(index=False))

    print("\n── Conversion Rate ─────────────────────────────")
    print(get_conversion_rate().to_string(index=False))

    print("\n── Step-wise Drop-off ──────────────────────────")
    print(get_stepwise_dropoff().to_string(index=False))

    print("\n── Device Breakdown ────────────────────────────")
    print(get_device_breakdown().to_string(index=False))

    print("\n── Device Share ────────────────────────────────")
    print(get_device_share().to_string(index=False))

    print("\n── Source Performance ──────────────────────────")
    print(get_source_performance().to_string(index=False))

    print("\n── Bounce by Source ────────────────────────────")
    print(get_bounce_by_source().to_string(index=False))

    print("\n── Top Pages ───────────────────────────────────")
    print(get_top_pages(10).to_string(index=False))

    print("\n── Converter Profile ───────────────────────────")
    print(get_converter_profile().to_string(index=False))