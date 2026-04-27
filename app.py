import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ads Performance Dashboard", layout="wide")

st.title("Ads Performance AI Dashboard")
st.write("Upload your Meta Ads or Google Ads CSV file to analyse campaign performance.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data Preview")
    st.dataframe(df)

    st.subheader("Select Columns")

    columns = df.columns.tolist()

    spend_col = st.selectbox("Select Spend Column", columns)
    impression_col = st.selectbox("Select Impressions Column", columns)
    reach_col = st.selectbox("Select Reach Column", columns)
    click_col = st.selectbox("Select Clicks Column", columns)
    campaign_col = st.selectbox("Select Campaign Name Column", columns)

    # Convert selected columns to numbers
    df[spend_col] = pd.to_numeric(df[spend_col], errors="coerce")
    df[impression_col] = pd.to_numeric(df[impression_col], errors="coerce")
    df[reach_col] = pd.to_numeric(df[reach_col], errors="coerce")
    df[click_col] = pd.to_numeric(df[click_col], errors="coerce")

    total_spend = df[spend_col].sum()
    total_impressions = df[impression_col].sum()
    total_reach = df[reach_col].sum()
    total_clicks = df[click_col].sum()

    cpm = (total_spend / total_impressions) * 1000 if total_impressions > 0 else 0
    ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
    cpc = total_spend / total_clicks if total_clicks > 0 else 0
    cost_per_reach = total_spend / total_reach if total_reach > 0 else 0

    st.subheader("Overall Performance")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spend", f"₹{total_spend:,.2f}")
    col2.metric("Impressions", f"{total_impressions:,.0f}")
    col3.metric("Reach", f"{total_reach:,.0f}")
    col4.metric("Clicks", f"{total_clicks:,.0f}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("CPM", f"₹{cpm:.2f}")
    col6.metric("CTR", f"{ctr:.2f}%")
    col7.metric("CPC", f"₹{cpc:.2f}")
    col8.metric("Cost per Reach", f"₹{cost_per_reach:.4f}")

    st.subheader("Campaign-wise Performance")

    campaign_summary = df.groupby(campaign_col).agg({
        spend_col: "sum",
        impression_col: "sum",
        reach_col: "sum",
        click_col: "sum"
    }).reset_index()

    campaign_summary["CPM"] = (campaign_summary[spend_col] / campaign_summary[impression_col]) * 1000
    campaign_summary["CTR (%)"] = (campaign_summary[click_col] / campaign_summary[impression_col]) * 100
    campaign_summary["CPC"] = campaign_summary[spend_col] / campaign_summary[click_col]

    st.dataframe(campaign_summary)

    st.subheader("Spend by Campaign")
    st.bar_chart(campaign_summary.set_index(campaign_col)[spend_col])

    st.subheader("Reach by Campaign")
    st.bar_chart(campaign_summary.set_index(campaign_col)[reach_col])

    st.subheader("Basic Recommendation")

    best_campaign = campaign_summary.sort_values("CTR (%)", ascending=False).iloc[0]
    high_cpm_campaign = campaign_summary.sort_values("CPM", ascending=False).iloc[0]

    st.success(f"Best campaign by CTR: {best_campaign[campaign_col]}")
    st.warning(f"Campaign with highest CPM: {high_cpm_campaign[campaign_col]}")

    st.subheader("Report Summary")

    summary = f"""
    Total ad spend was ₹{total_spend:,.2f}, generating {total_impressions:,.0f} impressions, 
    {total_reach:,.0f} reach, and {total_clicks:,.0f} clicks. 
    The overall CPM was ₹{cpm:.2f}, CTR was {ctr:.2f}%, and CPC was ₹{cpc:.2f}. 
    The best-performing campaign based on CTR was {best_campaign[campaign_col]}.
    """

    st.write(summary)

else:
    st.info("Please upload a CSV file to start analysis.")
