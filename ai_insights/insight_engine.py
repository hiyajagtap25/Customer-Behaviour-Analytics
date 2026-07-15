import os
from dotenv import load_dotenv
from groq import Groq

from ai_insights.cache import (
    load_cache,
    save_cache,
    clear_cache
)

from ai_insights.prompts import (
    funnel_prompt,
    device_prompt,
    source_prompt,
    page_prompt
)

from database.db_queries import (
    get_funnel_summary,
    get_conversion_rate,
    get_device_breakdown,
    get_source_performance,
    get_bounce_by_source,
    get_top_pages,
    get_converter_profile,
    get_stage_reach
)


# ══════════════════════════════════════════════════════════════
# LOAD ENV VARIABLES
# ══════════════════════════════════════════════════════════════

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ══════════════════════════════════════════════════════════════
# GENERIC AI CALL
# ══════════════════════════════════════════════════════════════

def generate_insight(prompt):
    """
    Sends prompt to Groq API and returns AI response.
    """

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior ecommerce conversion analyst. "
                        "Give concise, business-focused, actionable insights. "
                        "Only use the data provided."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.6,
            max_tokens=220
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI insight unavailable: {str(e)}"


# ══════════════════════════════════════════════════════════════
# FUNNEL INSIGHT
# ══════════════════════════════════════════════════════════════

def get_funnel_insight(refresh=True):

    cache = load_cache()

    if not refresh and "funnel" in cache:
        print("[funnel] Using cached insight.")
        return cache["funnel"]

    print("[funnel] Generating insight...")

    funnel_df = get_funnel_summary()

    conversion_df = get_conversion_rate()

    conversion_row = conversion_df.iloc[0]

    prompt = funnel_prompt(
        funnel_df=funnel_df,
        conversion_row=conversion_row
    )

    insight = generate_insight(prompt)

    cache["funnel"] = insight

    save_cache(cache)

    print("[funnel] Done and cached.")

    return insight


# ══════════════════════════════════════════════════════════════
# DEVICE INSIGHT
# ══════════════════════════════════════════════════════════════

def get_device_insight(refresh=True):

    cache = load_cache()

    if not refresh and "device" in cache:
        print("[device] Using cached insight.")
        return cache["device"]

    print("[device] Generating insight...")

    device_df = get_device_breakdown()

    prompt = device_prompt(device_df)

    insight = generate_insight(prompt)

    cache["device"] = insight

    save_cache(cache)

    print("[device] Done and cached.")

    return insight


# ══════════════════════════════════════════════════════════════
# SOURCE INSIGHT
# ══════════════════════════════════════════════════════════════

def get_source_insight(refresh=True):

    cache = load_cache()

    if not refresh and "source" in cache:
        print("[source] Using cached insight.")
        return cache["source"]

    print("[source] Generating insight...")

    source_df = get_source_performance()

    bounce_df = get_bounce_by_source()

    converter_df = get_converter_profile()

    # Add top converter profile context
    top_converter = (
        converter_df.iloc[0].to_dict()
        if not converter_df.empty
        else None
    )

    prompt = source_prompt(
        source_df=source_df,
        bounce_df=bounce_df
    )

    if top_converter:
        prompt += f"""

TOP CONVERTER PROFILE:
- Device: {top_converter['device_type']}
- Source: {top_converter['source_group']}
- Converted Sessions: {top_converter['converted_sessions']}
"""

    insight = generate_insight(prompt)

    cache["source"] = insight

    save_cache(cache)

    print("[source] Done and cached.")

    return insight


# ══════════════════════════════════════════════════════════════
# PAGE INSIGHT
# ══════════════════════════════════════════════════════════════

def get_page_insight(refresh=True):

    cache = load_cache()

    if not refresh and "page" in cache:
        print("[page] Using cached insight.")
        return cache["page"]

    print("[page] Generating insight...")

    funnel_df = get_funnel_summary()

    top_pages_df = get_top_pages()

    stage_df = get_stage_reach()

    prompt = page_prompt(
        funnel_df=funnel_df,
        top_pages_df=top_pages_df
    )

    # Add stage reach context
    if not stage_df.empty:

        stage_summary = stage_df.to_string(index=False)

        prompt += f"""

STAGE REACH DATA:
{stage_summary}
"""

    insight = generate_insight(prompt)

    cache["page"] = insight

    save_cache(cache)

    print("[page] Done and cached.")

    return insight


# ══════════════════════════════════════════════════════════════
# GET ALL INSIGHTS
# ══════════════════════════════════════════════════════════════

def get_all_insights(refresh=True):

    return {
        "funnel": get_funnel_insight(refresh),
        "device": get_device_insight(refresh),
        "source": get_source_insight(refresh),
        "page": get_page_insight(refresh)
    }


# ══════════════════════════════════════════════════════════════
# REFRESH ALL INSIGHTS
# ══════════════════════════════════════════════════════════════

def refresh_all_insights():

    print("\nRefreshing all AI insights...\n")

    clear_cache()

    insights = get_all_insights(refresh=True)

    print("\nAll insights refreshed.\n")

    return insights


# ══════════════════════════════════════════════════════════════
# STANDALONE TEST
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    insights = get_all_insights()

    print("\n" + "=" * 70)
    print("FUNNEL INSIGHT")
    print("=" * 70)
    print(insights["funnel"])

    print("\n" + "=" * 70)
    print("DEVICE INSIGHT")
    print("=" * 70)
    print(insights["device"])

    print("\n" + "=" * 70)
    print("SOURCE INSIGHT")
    print("=" * 70)
    print(insights["source"])

    print("\n" + "=" * 70)
    print("PAGE INSIGHT")
    print("=" * 70)
    print(insights["page"])