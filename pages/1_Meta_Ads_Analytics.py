import pandas as pd
import streamlit as st

st.set_page_config(page_title="Meta Ads Analytics", layout="wide")


def safe_divide(numerator, denominator):
    if denominator is None or denominator == 0 or pd.isna(denominator):
        return 0
    return numerator / denominator


def money(value):
    return f"${value:,.2f}"


def number(value):
    return f"{value:,.0f}"


def percent(value):
    return f"{value:.2f}%"


def find_column(columns, possible_names):
    clean_columns = {col.lower().strip(): col for col in columns}

    for name in possible_names:
        if name.lower().strip() in clean_columns:
            return clean_columns[name.lower().strip()]

    for col in columns:
        col_clean = col.lower().strip()
        for name in possible_names:
            if name.lower().strip() in col_clean:
                return col

    return None


def select_column(label, columns, possible_names, required=True):
    guessed_column = find_column(columns, possible_names)

    if required:
        options = list(columns)
        default_index = options.index(guessed_column) if guessed_column in options else 0
    else:
        options = ["Not available"] + list(columns)
        default_index = options.index(guessed_column) if guessed_column in options else 0

    return st.selectbox(label, options, index=default_index)


def numeric_series(df, column):
    if column is None or column == "Not available":
        return pd.Series([0] * len(df), index=df.index)

    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def clickable_url(url):
    if pd.isna(url) or str(url).strip() == "":
        return ""

    clean_url = str(url).strip()
    return f'<a href="{clean_url}" target="_blank">Open post</a>'


sample_meta_csv = """Campaign name,Ad name,Post URL,Spend,Reach,Impressions,Clicks,Engagements,Date
Awareness Campaign,Video Ad 1,https://facebook.com/post1,120,5000,8000,140,620,2026-04-01
Sales Campaign,Carousel Ad 1,https://facebook.com/post2,250,7200,12000,310,890,2026-04-02
Retargeting Campaign,Image Ad 1,https://facebook.com/post3,90,2600,4100,85,210,2026-04-03
"""

st.title("Meta Ads Analytics")
st.write("Upload a Meta Ads CSV export. The app will automatically detect common column names where possible.")

st.download_button(
    label="Download sample Meta CSV",
    data=sample_meta_csv,
    file_name="sample_meta_ads.csv",
    mime="text/csv",
)

uploaded_file = st.file_uploader("Upload Meta Ads CSV", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to begin.")
    st.stop()

try:
    raw_df = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"Could not read CSV file: {error}")
    st.stop()

if raw_df.empty:
    st.warning("The uploaded CSV file is empty.")
    st.stop()

columns = raw_df.columns.tolist()

st.subheader("Map CSV Columns")
st.caption("Columns are auto-detected when possible. Please check each dropdown before reviewing results.")

col1, col2 = st.columns(2)

with col1:
    campaign_col = select_column(
        "Campaign name",
        columns,
        ["campaign name", "campaign", "campaign_name", "campaign_name_text"],
    )
    ad_col = select_column(
        "Ad name",
        columns,
        ["ad name", "ad", "ad_name", "creative", "post name"],
    )
    post_url_col = select_column(
        "Post URL",
        columns,
        ["post url", "post_url", "url", "permalink", "link", "ad url"],
        required=False,
    )
    spend_col = select_column(
        "Spend",
        columns,
        ["spend", "amount spent", "amount_spent", "cost", "ad spend"],
    )
    date_col = select_column(
        "Date",
        columns,
        ["date", "day", "reporting starts", "start date"],
        required=False,
    )

with col2:
    reach_col = select_column(
        "Reach",
        columns,
        ["reach", "people reached"],
    )
    impressions_col = select_column(
        "Impressions",
        columns,
        ["impressions", "views"],
    )
    clicks_col = select_column(
        "Clicks",
        columns,
        ["clicks", "link clicks", "click", "outbound clicks"],
    )
    engagements_col = select_column(
        "Engagements",
        columns,
        ["engagements", "post engagements", "post engagement", "reactions", "interactions"],
    )

df = pd.DataFrame()
df["Campaign"] = raw_df[campaign_col].fillna("Unknown campaign").astype(str)
df["Ad"] = raw_df[ad_col].fillna("Unknown ad").astype(str)
df["Post URL"] = raw_df[post_url_col] if post_url_col != "Not available" else ""
df["Spend"] = numeric_series(raw_df, spend_col)
df["Reach"] = numeric_series(raw_df, reach_col)
df["Impressions"] = numeric_series(raw_df, impressions_col)
df["Clicks"] = numeric_series(raw_df, clicks_col)
df["Engagements"] = numeric_series(raw_df, engagements_col)

if date_col != "Not available":
    df["Date"] = pd.to_datetime(raw_df[date_col], errors="coerce")

    valid_dates = df["Date"].dropna()
    if not valid_dates.empty:
        st.subheader("Date Filter")
        start_date, end_date = st.date_input(
            "Select date range",
            value=(valid_dates.min().date(), valid_dates.max().date()),
        )

        df = df[
            (df["Date"].dt.date >= start_date)
            & (df["Date"].dt.date <= end_date)
        ]

if df.empty:
    st.warning("No rows match the selected filters.")
    st.stop()

total_spend = df["Spend"].sum()
total_reach = df["Reach"].sum()
total_impressions = df["Impressions"].sum()
total_clicks = df["Clicks"].sum()
total_engagements = df["Engagements"].sum()

cpm = safe_divide(total_spend, total_impressions) * 1000
ctr = safe_divide(total_clicks, total_impressions) * 100
cpc = safe_divide(total_spend, total_clicks)
cost_per_reach = safe_divide(total_spend, total_reach)
cost_per_engagement = safe_divide(total_spend, total_engagements)

st.subheader("Performance Overview")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Spend", money(total_spend))
m2.metric("Total Reach", number(total_reach))
m3.metric("Impressions", number(total_impressions))
m4.metric("Clicks", number(total_clicks))
m5.metric("Engagements", number(total_engagements))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("CPM", money(cpm))
m2.metric("CTR", percent(ctr))
m3.metric("CPC", money(cpc))
m4.metric("Cost per Reach", money(cost_per_reach))
m5.metric("Cost per Engagement", money(cost_per_engagement))

campaign_table = df.groupby("Campaign", as_index=False).agg(
    Spend=("Spend", "sum"),
    Reach=("Reach", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Engagements=("Engagements", "sum"),
)

campaign_table["CPM"] = campaign_table.apply(
    lambda row: safe_divide(row["Spend"], row["Impressions"]) * 1000,
    axis=1,
)
campaign_table["CTR"] = campaign_table.apply(
    lambda row: safe_divide(row["Clicks"], row["Impressions"]) * 100,
    axis=1,
)
campaign_table["CPC"] = campaign_table.apply(
    lambda row: safe_divide(row["Spend"], row["Clicks"]),
    axis=1,
)

ad_table = df.groupby(["Campaign", "Ad", "Post URL"], as_index=False).agg(
    Spend=("Spend", "sum"),
    Reach=("Reach", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Engagements=("Engagements", "sum"),
)

ad_table["CTR"] = ad_table.apply(
    lambda row: safe_divide(row["Clicks"], row["Impressions"]) * 100,
    axis=1,
)
ad_table["Post Link"] = ad_table["Post URL"].apply(clickable_url)

st.subheader("Campaign-wise Table")
st.dataframe(
    campaign_table.sort_values("Spend", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Ad/Post-wise Table")
display_table = ad_table.drop(columns=["Post URL"])
st.markdown(display_table.to_html(escape=False, index=False), unsafe_allow_html=True)

st.subheader("Charts")

c1, c2 = st.columns(2)
with c1:
    st.write("Spend by Campaign")
    st.bar_chart(campaign_table.set_index("Campaign")["Spend"])

with c2:
    st.write("Reach by Campaign")
    st.bar_chart(campaign_table.set_index("Campaign")["Reach"])

st.write("Engagements by Post/Ad")
st.bar_chart(ad_table.set_index("Ad")["Engagements"])

st.subheader("Recommendations")

best_campaign_ctr = campaign_table.loc[campaign_table["CTR"].idxmax()]
best_post = ad_table.loc[ad_table["Engagements"].idxmax()]
highest_cpm = campaign_table.loc[campaign_table["CPM"].idxmax()]
lowest_ctr = campaign_table.loc[campaign_table["CTR"].idxmin()]

st.success(f"Best campaign by CTR: {best_campaign_ctr['Campaign']} with {percent(best_campaign_ctr['CTR'])}.")
st.success(f"Best post by engagement: {best_post['Ad']} with {number(best_post['Engagements'])} engagements.")
st.warning(f"Campaign with highest CPM: {highest_cpm['Campaign']} at {money(highest_cpm['CPM'])}.")
st.warning(f"Campaign with lowest CTR: {lowest_ctr['Campaign']} at {percent(lowest_ctr['CTR'])}.")

st.subheader("Report Summary")
st.write(
    f"Your Meta Ads data includes {len(df)} rows across {campaign_table['Campaign'].nunique()} campaigns. "
    f"Total spend was {money(total_spend)}, generating {number(total_impressions)} impressions, "
    f"{number(total_clicks)} clicks, and {number(total_engagements)} engagements. "
    f"Overall CTR was {percent(ctr)}, CPC was {money(cpc)}, and CPM was {money(cpm)}."
)
