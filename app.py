import streamlit as st

st.set_page_config(
    page_title="Ads Performance AI Dashboard",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.6rem;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }
        .subtitle {
            color: #5f6b7a;
            font-size: 1.08rem;
            max-width: 760px;
            margin-bottom: 2rem;
        }
        div.stButton > button {
            width: 100%;
            min-height: 132px;
            border: 1px solid #d9e1ec;
            border-radius: 8px;
            background: #ffffff;
            font-size: 1.25rem;
            font-weight: 650;
            color: #1f2937;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        }
        div.stButton > button:hover {
            border-color: #2563eb;
            color: #1d4ed8;
            background: #f8fbff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Ads Performance AI Dashboard</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="subtitle">
        Upload manual CSV exports from Meta Ads or Google Ads, map your columns,
        and quickly review campaign performance, charts, recommendations, and a simple report summary.
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    if st.button("Meta Ads Analytics"):
        st.switch_page("pages/1_Meta_Ads_Analytics.py")

with right:
    if st.button("Google Ads Analytics"):
        st.switch_page("pages/2_Google_Ads_Analytics.py")

st.info("Choose an analytics page, upload your CSV, and map your columns.")
