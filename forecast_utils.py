import pandas as pd
from prophet import Prophet
from meteostat import Daily, Point
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st

def preprocess_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip().str.lower()

    required_cols = ['date', 'rep name', 'product', 'region', 'qty']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        st.stop()

    df.rename(columns={'rep name': 'rep', 'qty': 'quantity'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df = df[['date', 'product', 'rep', 'region', 'quantity']]
    df['day_of_week'] = df['date'].dt.day_name()

    location = Point(31.5204, 74.3587)  # Lahore
    start = df['date'].min().to_pydatetime()
    end = df['date'].max().to_pydatetime()
    weather = Daily(location, start, end).fetch().reset_index()
    weather = weather[['time', 'tavg']].rename(columns={'time': 'date', 'tavg': 'temperature'})
    df = pd.merge(df, weather, on='date', how='left')

    return df

def forecast_sales(df):
    daily = df.groupby('date')['quantity'].sum().reset_index()
    daily.columns = ['ds', 'y']
    model = Prophet(daily_seasonality=True)
    model.fit(daily)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], model

def plot_forecast(forecast_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], name='Forecast'))
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_upper'], name='Upper Bound', line=dict(dash='dot')))
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_lower'], name='Lower Bound', line=dict(dash='dot')))
    fig.update_layout(title='📈 Forecasted Sales', xaxis_title='Date', yaxis_title='Quantity')
    return fig

def calculate_target_analysis(df, forecast_df, target_value, target_type):
    today = pd.to_datetime(datetime.today().date())
    if target_type == 'Monthly':
        current = df[df['date'].dt.month == today.month]['quantity'].sum()
    else:
        current = df['quantity'].sum()
    forecast = forecast_df[forecast_df['ds'] >= today]['yhat'].sum()
    total = current + forecast
    remaining = max(0, target_value - current)
    days_left = (forecast_df['ds'].max() - today).days
    per_day = round(remaining / days_left, 2) if days_left > 0 else 0
    pct = round((total / target_value) * 100, 2)
    return {
        "Target": target_value,
        "Current Sales": round(current, 2),
        "Forecasted": round(forecast, 2),
        "Projected Total": round(total, 2),
        "Required per Day": per_day,
        "Projected % of Target": pct
    }

def generate_recommendations(analysis):
    if analysis['Projected % of Target'] >= 100:
        return "✅ You're on track to meet or exceed your target!"
    return f"🚀 You need to sell {analysis['Required per Day']} units/day to hit your goal."


