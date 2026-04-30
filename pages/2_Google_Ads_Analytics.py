import pandas as pd
import streamlit as st

st.set_page_config(page_title="Google Ads Analytics", layout="wide")

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

st.title("Google Ads Analytics")
st.write("Upload a Google Ads CSV export and map your columns.")

uploaded_file = st.file_uploader("Upload Google Ads CSV", type=["csv"])

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
    ad_group_col = choose_column("Ad group name", columns, required=False)
    cost_col = choose_column("Spend / cost", columns)

with col2:
    impressions_col = choose_column("Impressions", columns)
    clicks_col = choose_column("Clicks", columns)
    conversions_col = choose_column("Conversions", columns, required=False)

df = pd.DataFrame()
df["Campaign"] = raw_df[campaign_col].fillna("Unknown campaign").astype(str)
df["Ad Group"] = raw_df[ad_group_col].fillna("Not available").astype(str) if ad_group_col != "Not available" else "Not available"
df["Cost"] = numeric_series(raw_df, cost_col)
df["Impressions"] = numeric_series(raw_df, impressions_col)
df["Clicks"] = numeric_series(raw_df, clicks_col)
df["Conversions"] = numeric_series(raw_df, conversions_col)

total_cost = df["Cost"].sum()
total_impressions = df["Impressions"].sum()
total_clicks = df["Clicks"].sum()
total_conversions = df["Conversions"].sum()

ctr = safe_divide(total_clicks, total_impressions) * 100
cpc = safe_divide(total_cost, total_clicks)
cpm = safe_divide(total_cost, total_impressions) * 1000
conversion_rate = safe_divide(total_conversions, total_clicks) * 100
cost_per_conversion = safe_divide(total_cost, total_conversions)

st.subheader("Performance Overview")

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Cost", money(total_cost))
m2.metric("Impressions", number(total_impressions))
m3.metric("Clicks", number(total_clicks))
m4.metric("CTR", percent(ctr))
m5.metric("CPC", money(cpc))
m6.metric("CPM", money(cpm))

if conversions_col != "Not available":
    c1, c2, c3 = st.columns(3)
    c1.metric("Conversions", number(total_conversions))
    c2.metric("Conversion Rate", percent(conversion_rate))
    c3.metric("Cost per Conversion", money(cost_per_conversion))

campaign_table = df.groupby("Campaign", as_index=False).agg(
    Cost=("Cost", "sum"),
    Impressions=("Impressions", "sum"),
    Clicks=("Clicks", "sum"),
    Conversions=("Conversions", "sum"),
)

campaign_table["CTR"] = campaign_table.apply(
    lambda row: safe_divide(row["Clicks"], row["Impressions"]) * 100,
    axis=1,
)
campaign_table["CPC"] = campaign_table.apply(
    lambda row: safe_divide(row["Cost"], row["Clicks"]),
    axis=1,
)
campaign_table["CPM"] = campaign_table.apply(
    lambda row: safe_divide(row["Cost"], row["Impressions"]) * 1000,
    axis=1,
)

if conversions_col != "Not available":
    campaign_table["Conversion Rate"] = campaign_table.apply(
        lambda row: safe_divide(row["Conversions"], row["Clicks"]) * 100,
        axis=1,
    )
    campaign_table["Cost per Conversion"] = campaign_table.apply(
        lambda row: safe_divide(row["Cost"], row["Conversions"]),
        axis=1,
    )
else:
    campaign_table = campaign_table.drop(columns=["Conversions"])

st.subheader("Campaign-wise Table")
st.dataframe(campaign_table.sort_values("Cost", ascending=False), use_container_width=True)

st.subheader("Charts")

c1, c2 = st.columns(2)
with c1:
    st.write("Cost by Campaign")
    st.bar_chart(campaign_table.set_index("Campaign")["Cost"])

with c2:
    st.write("Clicks by Campaign")
    st.bar_chart(campaign_table.set_index("Campaign")["Clicks"])

st.write("CTR by Campaign")
st.bar_chart(campaign_table.set_index("Campaign")["CTR"])

st.subheader("Recommendations")

best_ctr = campaign_table.loc[campaign_table["CTR"].idxmax()]
highest_cost = campaign_table.loc[campaign_table["Cost"].idxmax()]
lowest_ctr = campaign_table.loc[campaign_table["CTR"].idxmin()]

st.success(f"Best campaign by CTR: {best_ctr['Campaign']} with {percent(best_ctr['CTR'])}.")
st.warning(f"Highest cost campaign: {highest_cost['Campaign']} with {money(highest_cost['Cost'])} spent.")
st.warning(f"Lowest CTR campaign: {lowest_ctr['Campaign']} at {percent(lowest_ctr['CTR'])}.")

st.subheader("Report Summary")

summary = (
    f"Your Google Ads data includes {len(df)} rows across {campaign_table['Campaign'].nunique()} campaigns. "
    f"Total cost was {money(total_cost)}, generating {number(total_impressions)} impressions "
    f"and {number(total_clicks)} clicks. Overall CTR was {percent(ctr)}, CPC was {money(cpc)}, "
    f"and CPM was {money(cpm)}."
)

if conversions_col != "Not available":
    summary += (
        f" The account generated {number(total_conversions)} conversions, with a conversion rate of "
        f"{percent(conversion_rate)} and cost per conversion of {money(cost_per_conversion)}."
    )

st.write(summary)
