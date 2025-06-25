
import streamlit as st
import pandas as pd
from forecast_utils import (
    preprocess_data, forecast_sales, plot_forecast,
    calculate_target_analysis, generate_recommendations
)

st.set_page_config(page_title="📊 Sales Forecast & Target Tracker", layout="wide")
st.title("📊 Sales Forecast & Target Tracker")

uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])
data = None

if uploaded_file:
    data = preprocess_data(uploaded_file)
    st.success("✅ Data loaded and enriched!")

if data is not None:
    rep = st.selectbox("Filter by Rep", ["All"] + sorted(data['rep'].unique()))
    product = st.selectbox("Filter by Product", ["All"] + sorted(data['product'].unique()))
    region = st.selectbox("Filter by Region", ["All"] + sorted(data['region'].unique()))

    df = data.copy()
    if rep != "All":
        df = df[df['rep'] == rep]
    if product != "All":
        df = df[df['product'] == product]
    if region != "All":
        df = df[df['region'] == region]

    forecast_df, model = forecast_sales(df)
    st.plotly_chart(plot_forecast(forecast_df), use_container_width=True)

    target_type = st.radio("Target Type", ["Monthly", "Yearly"])
    target_value = st.number_input("Enter Sales Target", step=10)

    if target_value:
        analysis = calculate_target_analysis(df, forecast_df, target_value, target_type)
        st.write(analysis)
        st.success(generate_recommendations(analysis))
