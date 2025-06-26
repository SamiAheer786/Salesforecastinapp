import streamlit as st
import pandas as pd
from forecast_utils import (
    preprocess_data, forecast_sales, plot_forecast,
    calculate_target_analysis, generate_recommendations
)

st.set_page_config(page_title="📊 Sales Forecast & Target Tracker", layout="wide")
st.title("🍦 Hico Ice Cream | Sales Forecast & Target Tracker")

uploaded_file = st.file_uploader("📤 Upload Sales CSV or Excel File", type=["csv", "xlsx"])
data = None

if uploaded_file:
    data = preprocess_data(uploaded_file)
    st.success("✅ Data loaded and enriched with weather & weekday info!")

if data is not None:
    st.sidebar.header("📌 Apply Filters")
    rep = st.sidebar.selectbox("Rep", ["All"] + sorted(data['rep'].unique()))
    product = st.sidebar.selectbox("Product", ["All"] + sorted(data['product'].unique()))
    region = st.sidebar.selectbox("Region", ["All"] + sorted(data['region'].unique()))

    df = data.copy()
    if rep != "All":
        df = df[df['rep'] == rep]
    if product != "All":
        df = df[df['product'] == product]
    if region != "All":
        df = df[df['region'] == region]

    forecast_df, model = forecast_sales(df)
    st.subheader("📊 Forecast Visualization")
    st.plotly_chart(plot_forecast(forecast_df), use_container_width=True)

    st.markdown("---")
    st.subheader("🎯 Target Analysis")
    target_type = st.radio("Target Type", ["Monthly", "Yearly"])
    target_value = st.number_input("Enter Sales Target (in Quantity)", step=100)

    if target_value:
        analysis = calculate_target_analysis(df, forecast_df, target_value, target_type)
        st.metric(label="📌 Projected Total Sales", value=f"{analysis['Projected Total']} units")
        st.metric(label="📊 % of Target", value=f"{analysis['Projected % of Target']}%")
        st.write(analysis)
        st.success(generate_recommendations(analysis))
else:
    st.info("👋 Upload your sales data to get started.")

