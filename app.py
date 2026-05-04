import streamlit as st

st.set_page_config(
    page_title="Ads Performance AI Dashboard",
    layout="wide",
)
st.markdown(
    """
    <style>
        .stApp {
            background: #f6f8fb;
        }

        .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        .main-title {
            font-size: 2.7rem;
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.35rem;
        }

        .subtitle {
            color: #5f6b7a;
            font-size: 1.08rem;
            max-width: 800px;
            margin-bottom: 2rem;
            line-height: 1.65;
        }

        div.stButton > button {
            width: 100%;
            min-height: 150px;
            border: 1px solid #d9e1ec;
            border-radius: 12px;
            background: #ffffff;
            font-size: 1.3rem;
            font-weight: 700;
            color: #111827;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            border-color: #2563eb;
            color: #1d4ed8;
            background: #f8fbff;
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.14);
        }

        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
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
