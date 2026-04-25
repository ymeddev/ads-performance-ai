import streamlit as st
import pandas as pd

st.title("Ads Performance AI Assistant")

uploaded_file = st.file_uploader(
    "Upload Meta Ads or Google Ads CSV File",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df)

    st.subheader("Basic Summary")
    st.write(df.describe())
