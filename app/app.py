"""
app.py
------
The Flask web application.

Routes:
    /           → Dashboard  (funnel chart + KPI cards + AI insight)
    /devices    → Device analysis (mobile vs desktop breakdown)
    /sources    → Traffic source analysis
    /insights   → All 4 AI insights on one page
    /api/refresh-insights → Clears cache and regenerates all insights (POST)

Run with:
    cd app
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import sys
import os

# Make parent folder importable so we can reach database/ and ai_insights/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, jsonify, request
from database.db_queries import (
    get_funnel_summary,
    get_conversion_rate,
    get_stepwise_dropoff,
    get_device_breakdown,
    get_device_share,
    get_source_performance,
    get_bounce_by_source,
    get_top_pages,
    get_converter_profile,
)
from ai_insights.insight_engine import get_all_insights, get_insight
from ai_insights.cache import clear_cache

app = Flask(__name__)


# ─────────────────────────────────────────────────
# Helper: convert DataFrame to list of dicts for templates
# ─────────────────────────────────────────────────

def df_to_list(df):
    return df.to_dict(orient='records')


# ─────────────────────────────────────────────────
# ROUTE 1: Dashboard
# ─────────────────────────────────────────────────

@app.route("/")
def dashboard():
    # KPI cards
    kpis         = get_conversion_rate().iloc[0].to_dict()

    # Funnel chart data
    funnel       = df_to_list(get_funnel_summary())

    # Step-wise drop-off table
    stepwise     = df_to_list(get_stepwise_dropoff())

    # Top pages table
    top_pages    = df_to_list(get_top_pages(8))

    # Funnel AI insight (uses cache if available)
    funnel_insight = get_insight('funnel')

    return render_template(
        "index.html",
        kpis           = kpis,
        funnel         = funnel,
        stepwise       = stepwise,
        top_pages      = top_pages,
        funnel_insight = funnel_insight,
    )


# ─────────────────────────────────────────────────
# ROUTE 2: Device Analysis
# ─────────────────────────────────────────────────

@app.route("/devices")
def devices():
    device_breakdown = df_to_list(get_device_breakdown())
    device_share     = df_to_list(get_device_share())
    device_insight   = get_insight('device')

    return render_template(
        "devices.html",
        device_breakdown = device_breakdown,
        device_share     = device_share,
        device_insight   = device_insight,
    )


# ─────────────────────────────────────────────────
# ROUTE 3: Traffic Sources
# ─────────────────────────────────────────────────

@app.route("/sources")
def sources():
    source_perf    = df_to_list(get_source_performance())
    bounce_by_src  = df_to_list(get_bounce_by_source())
    converters     = df_to_list(get_converter_profile())
    source_insight = get_insight('source')

    return render_template(
        "sources.html",
        source_perf    = source_perf,
        bounce_by_src  = bounce_by_src,
        converters     = converters,
        source_insight = source_insight,
    )


# ─────────────────────────────────────────────────
# ROUTE 4: All Insights
# ─────────────────────────────────────────────────

@app.route("/insights")
def insights():
    all_insights = get_all_insights()
    return render_template("insights.html", insights=all_insights)


# ─────────────────────────────────────────────────
# ROUTE 5: Refresh Insights (POST)
# Called by the "Regenerate" button on insights page
# ─────────────────────────────────────────────────

@app.route("/api/refresh-insights", methods=["POST"])
def refresh_insights():
    try:
        clear_cache()
        new_insights = get_all_insights(force_refresh=True)
        return jsonify({"status": "ok", "insights": new_insights})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)