def funnel_prompt(funnel_df, conversion_row):
    # Pull numbers from the DataFrames
    rows = funnel_df.set_index('drop_off')
    bounce_pct  = rows.loc['Bounce', 'pct_of_total']
    product_pct = rows.loc['Dropped at Product', 'pct_of_total']
    cart_pct    = rows.loc['Dropped at Cart', 'pct_of_total']
    checkout_pct= rows.loc['Reached Checkout', 'pct_of_total']

    total       = conversion_row['total_sessions']
    conv_rate   = conversion_row['conversion_rate_pct']
    conversions = conversion_row['total_conversions']

    return f"""
You are a senior e-commerce conversion rate optimisation (CRO) analyst.
Analyse this funnel data and explain what is happening and why.

FUNNEL DATA:
- Total sessions      : {total}
- Bounced (home only) : {bounce_pct}% of sessions
- Dropped at Product  : {product_pct}% of sessions
- Dropped at Cart     : {cart_pct}% of sessions
- Reached Checkout    : {checkout_pct}% of sessions
- Overall conversions : {conversions} ({conv_rate}%)

YOUR TASK:
1. In 1 sentence, state the single biggest problem in this funnel.
2. In 2-3 sentences, explain the most likely reasons WHY users are dropping at the product page (the biggest drop-off point).
3. In 1 sentence, give one specific, actionable fix the team can implement this week.

Write in plain English. No bullet points. No markdown. No jargon.
Keep total response under 120 words.
""".strip()


def device_prompt(device_df):
    """
    Prompt for explaining mobile vs desktop performance gap.
    device_df: DataFrame from get_device_breakdown()
    """
    rows = device_df.set_index('device_type')

    desktop_sessions  = rows.loc['desktop', 'total_sessions']
    desktop_conv      = rows.loc['desktop', 'conv_rate_pct']
    desktop_bounced   = rows.loc['desktop', 'bounced']

    mobile_sessions   = rows.loc['mobile', 'total_sessions']
    mobile_conv       = rows.loc['mobile', 'conv_rate_pct']
    mobile_bounced    = rows.loc['mobile', 'bounced']

    gap = round(desktop_conv - mobile_conv, 2)

    return f"""
You are a senior e-commerce CRO analyst specialising in mobile UX.
Analyse this device performance data.

DEVICE DATA:
- Desktop: {desktop_sessions} sessions, {desktop_conv}% conversion, {desktop_bounced} bounces
- Mobile : {mobile_sessions} sessions, {mobile_conv}% conversion, {mobile_bounced} bounces
- Conversion gap: desktop is {gap}% higher than mobile

YOUR TASK:
1. In 1 sentence, state how serious the mobile problem is.
2. In 2 sentences, explain the most common reasons mobile users convert so much less than desktop users on e-commerce sites.
3. In 1 sentence, give one specific fix to try first.

Write in plain English. No bullet points. No markdown.
Keep total response under 120 words.
""".strip()


def source_prompt(source_df, bounce_df):
    """
    Prompt for explaining traffic source performance.
    source_df: DataFrame from get_source_performance()
    bounce_df : DataFrame from get_bounce_by_source()
    """
    # Build a readable summary of each source
    source_lines = []
    for _, row in source_df.iterrows():
        bounce_row = bounce_df[bounce_df['source_group'] == row['source_group']]
        bounce_rate = bounce_row['bounce_rate_pct'].values[0] if len(bounce_row) else 'N/A'
        source_lines.append(
            f"  {row['source_group']}: {row['total_sessions']} sessions, "
            f"{row['conv_rate_pct']}% conversion, {bounce_rate}% bounce"
        )
    source_summary = "\n".join(source_lines)

    return f"""
You are a senior e-commerce CRO analyst specialising in traffic quality.
Analyse this traffic source data.

SOURCE DATA:
{source_summary}

YOUR TASK:
1. In 1 sentence, identify which traffic source is the biggest problem and why.
2. In 2 sentences, explain why paid/partner traffic often has high bounce rates and low conversions.
3. In 1 sentence, give one actionable recommendation for improving traffic quality.

Write in plain English. No bullet points. No markdown.
Keep total response under 120 words.
""".strip()


def page_prompt(funnel_df, top_pages_df):
    """
    Prompt for page-level drop-off insight.
    funnel_df    : DataFrame from get_funnel_summary()
    top_pages_df : DataFrame from get_top_pages()
    """
    top_5 = top_pages_df.head(5)[['page', 'hits']].to_string(index=False)

    rows = funnel_df.set_index('drop_off')
    product_sessions = rows.loc['Dropped at Product', 'sessions']
    cart_sessions    = rows.loc['Dropped at Cart', 'sessions']

    return f"""
You are a senior e-commerce UX analyst.
Analyse these page-level patterns.

PAGE DATA:
- {product_sessions} sessions dropped at the product browsing stage (never added to cart)
- {cart_sessions} sessions dropped at cart (added to cart but never went to checkout)

TOP 5 MOST VISITED PAGES:
{top_5}

YOUR TASK:
1. In 1 sentence, explain what the product page drop-off pattern suggests about user intent.
2. In 2 sentences, explain the most common reasons users abandon carts before checkout.
3. In 1 sentence, give one specific fix to reduce cart abandonment.

Write in plain English. No bullet points. No markdown.
Keep total response under 120 words.
""".strip()