import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt 
from datetime import datetime 
import time 
# Ensure these functions are correctly defined in your main.py
from main import fetch_cme_data, extract_speed_and_time 

st.set_page_config(page_title="Space Weather Dashboard", layout="wide")

st.title("Real-Time Space Weather Dashboard") 
st.write(f"Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}") 

# Fetch Data
data = fetch_cme_data(days=7) 

if not data: 
    st.error("No raw data from NASA API — check your API key or connection.") 
    st.stop()

# Process Data
df = extract_speed_and_time(data) 

# Debug metrics
col1, col2 = st.columns(2)
col1.metric("CMEs Detected (7 Days)", len(df))

if df.empty: 
    st.warning("No CMEs detected in the last 7 days (solar activity can be quiet).") 
    st.stop() 

# Display Table
st.subheader("Recent CME Events")
st.dataframe(df[['time', 'speed', 'note']].head(10), use_container_width=True) 

# Plotting Logic
st.subheader("CME Speed Trend")
if df['speed'].notna().any():
    df_plot = df.dropna(subset=['speed']).copy() 
    df_plot['time'] = pd.to_datetime(df_plot['time']) 
    df_plot = df_plot.sort_values('time') 
    
    fig, ax = plt.subplots(figsize=(12, 6)) 
    ax.plot(df_plot['time'], df_plot['speed'], marker='o', linestyle='-', color='#ff4444') 
    ax.set_title("CME Speed (km/s)", fontsize=16) 
    ax.set_ylabel("Speed (km/s)") 
    ax.set_xlabel("Date (UTC)") 
    ax.grid(True, alpha=0.3) 
    plt.xticks(rotation=45) 
    plt.tight_layout() 
    st.pyplot(fig) 
else:
    st.info("No speed measurements available in this period to plot.") 

# Auto-refresh every 10 minutes 
st.divider()
st.write("Dashboard will auto-refresh in 10 minutes.")
time.sleep(600) 
st.rerun()
