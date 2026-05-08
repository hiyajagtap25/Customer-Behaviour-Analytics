import pandas as pd

#page classification for funnel
def classify_page(page):
    """
    Returns one of: 'home', 'product', 'cart', 'checkout', 'other'
    """
    page = str(page).lower()

    if page == '/home':
        return 'home'

    elif any(x in page for x in ['basket.html', 'shop.axd/cart', 'wishlist.html']):
        return 'cart'

    elif any(x in page for x in ['yourinfo.html', 'revieworder.html',
                                   'payment.html', 'ordercompleted.html']):
        return 'checkout'

    elif any(x in page for x in ['google+redesign', 'google redesign',
                                   'store.html', 'asearch.html', 'storeitem.html']):
        return 'product'

    else:
        return 'other'

#source classification

def classify_source(source):
    """
    Returns one of: 'Direct', 'YouTube', 'Google / Paid', 'Partners', 'Other'
    """
    source = str(source).lower()

    if 'google' in source or 'adwords' in source or 'dfa' in source:
        return 'Google / Paid'
    elif 'youtube' in source:
        return 'YouTube'
    elif 'direct' in source:
        return 'Direct'
    elif 'partner' in source:
        return 'Partners'
    else:
        return 'Other'


#Funnel Stage number

STAGE_ORDER = {
    'home'    : 1,
    'product' : 2,
    'cart'    : 3,
    'checkout': 4,
    'other'   : 0
}

DROP_OFF_LABEL = {
    1: 'Bounce',
    2: 'Dropped at Product',
    3: 'Dropped at Cart',
    4: 'Reached Checkout'
}



def build_session_row(group):
    """
    Input : all rows for one session_id
    Output: one summary row (a pd.Series)
    """
    cats = group['page_cat'].tolist()

    # Ignore 'other' pages for funnel logic
    meaningful = [c for c in cats if c != 'other']
    if not meaningful:
        return None                         # skip sessions with only 'other' pages

    # Find the deepest stage reached
    stage_nums = [STAGE_ORDER[p] for p in meaningful]
    max_stage  = max(stage_nums)
    last_step  = [k for k, v in STAGE_ORDER.items() if v == max_stage][0]

    return pd.Series({
        'device_type'   : group['device_type'].iloc[0],
        'source'        : group['source'].iloc[0],
        'source_group'  : group['source_group'].iloc[0],
        'page_sequence' : ','.join(cats),   # full journey: "home,product,cart"
        'last_step'     : last_step,
        'funnel_stage'  : max_stage,
        'drop_off'      : DROP_OFF_LABEL[max_stage],
        'converted'     : int(group['transactions'].sum() > 0)
    })


#main tranform function

def transform(df):
    """
    Runs all transformations on the raw DataFrame.

    Returns:
        raw_events     (DataFrame) — hit-level data with new columns added
        session_funnel (DataFrame) — one row per session
    """
    print("Transforming data...")

    # Step A — Classify every page hit and traffic source
    df['page_cat']     = df['page'].apply(classify_page)
    df['source_group'] = df['source'].apply(classify_source)

    print(f"\n  Page category counts:")
    for cat, count in df['page_cat'].value_counts().items():
        print(f"    {cat:<12} {count}")

    # Step B — Build the session-level funnel table
    print("\n  Building session funnel (one row per session)...")

    sessions = (
        df.groupby('session_id')
          .apply(build_session_row)
          .dropna()                 # drop sessions that had only 'other' pages
          .reset_index()            # session_id becomes a regular column
    )

    # Fix dtypes
    sessions['funnel_stage'] = sessions['funnel_stage'].astype(int)
    sessions['converted']    = sessions['converted'].astype(int)

    # Step C — Print summary
    total      = len(sessions)
    converted  = sessions['converted'].sum()
    conv_rate  = round(converted / total * 100, 2)

    print(f"\n  ── Results ──────────────────────")
    print(f"  Total sessions : {total}")
    print(f"  Conversions    : {converted}  ({conv_rate}%)")
    print(f"\n  Drop-off breakdown:")
    for label, count in sessions['drop_off'].value_counts().items():
        pct = round(count / total * 100, 1)
        print(f"    {label:<25} {count}  ({pct}%)")

    print(f"\n  Transform complete.\n")
    return df, sessions


# ─────────────────────────────────────────────
# Quick test — run this file directly to check
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from ingest import load_raw_data

    raw = load_raw_data(r"C:\Users\dell\Desktop\Customer-Behaviour-Analytics\data\raw.csv")
    raw_events, session_funnel = transform(raw)

    print("\nSample rows from session_funnel:")
    print(session_funnel[['session_id', 'device_type', 'source_group',
                           'last_step', 'drop_off', 'converted']].head(8).to_string())