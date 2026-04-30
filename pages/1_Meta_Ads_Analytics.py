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

def choose_column(label, columns, required=True):
    options = list(columns)
    if not required:
        options = ["Not available"] + options
    return st.selectbox(label, options)

def numeric_series(df, column):
    if column is None or column == "Not available":
        return pd.Series([0] * len(df), index=df.index)
    return pd.to_numeric(df[column], errors="coerce").fillna(0)

def clickable_url(url):
    if pd.isna(url) or str(url).strip() == "":
        return ""
    url = str(url).strip()
    return f'<a href="{url}" target="_blank">Open post</a>'

st.title("Meta Ads Analytics")
st.write("Upload a Meta Ads CSV export and map your columns.")

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

col1, col2 = st.columns(2)

with col1:
    campaign_col = choose_column("Campaign name", columns)
    ad_col = choose_column("Ad name", columns)
    post_url_col = choose_column("Post URL", columns, required=False)
    spend_col = choose_column("Spend", columns)

with col2:
    reach_col = choose_column("Reach", columns)
    impressions_col = choose_column("Impressions", columns)
    clicks_col = choose_column("Clicks", columns)
    engagements_col = choose_column("Engagements", columns)

df = pd.DataFrame()
df["Campaign"] = raw_df[campaign_col].fillna("Unknown campaign").astype(str)
df["Ad"] = raw_df[ad_col].fillna("Unknown ad").astype(str)
df["Post URL"] = raw_df[post_url_col] if post_url_col != "Not available" else ""
df["Spend"] = numeric_series(raw_df, spend_col)
df["Reach"] = numeric_series(raw_df, reach_col)
df["Impressions"] = numeric_series(raw_df, impressions_col)
df["Clicks"] = numeric_series(raw_df, clicks_col)
df["Engagements"] = numeric_series(raw_df, engagements_col)

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
st.dataframe(campaign_table.sort_values("Spend", ascending=False), use_container_width=True)

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
