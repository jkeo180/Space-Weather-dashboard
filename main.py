import requests
import time
from datetime import datetime, timedelta,timezone
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from os import getenv
from dotenv import load_dotenv
import json

from ui import fetch_cme_data
# ---------- ENV ----------
load_dotenv()
API_KEY = getenv("NASA_API_KEY")

if not API_KEY:
    st.error("NASA API key not found. Please set it in the .env file.")
    st.stop()

# ---------- DATA FETCH ----------
data = fetch_cme_data(days=30)

if not data:
    st.error("No raw data from NASA API — check your API key or connection.")
    st.stop()

df = pd.DataFrame(data)

# Step 1: Clean & lowercase column names
df.columns = df.columns.astype(str).str.strip().str.lower()

# Step 2: Rename actual NASA columns to what your code expects
df = df.rename(columns={
    'starttime': 'time',          # NASA gives "startTime"
    'cmeanalyses': 'cmeanalyses', # if you need it later
    'note': 'note'
})

# Step 3: Select only what you want (safe if missing)
expected_cols = df.columns.tolist() + ['time', 'speed', 'note']
available_cols = [col for col in expected_cols if col in df.columns]
if not available_cols:
    st.error("No expected columns found in data. Check NASA response.")
    st.stop()
if not expected_cols[0] in available_cols:
    st.warning(f"Expected 'time' column not found. Available columns: {available_cols}")
df = df[available_cols]

# Debug: show real columns
st.write("Available columns after cleanup:", list(df.columns))

st.write(f"**CMEs in last 7 days:** {len(df)}")
st.dataframe(df.head(10), use_container_width=True)

# Plot only if 'speed' exists
if 'speed' in df.columns and df['speed'].notna().any():
    df_plot = df.dropna(subset=['speed']).copy()
    df_plot['time'] = pd.to_datetime(df_plot['time'], errors='coerce')
    df_plot = df_plot.sort_values('time')

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_plot['time'], df_plot['speed'], marker='o')
    ax.set_title("CME Speed Over Last 7 Days (km/s)")
    ax.set_ylabel("Speed (km/s)")
    ax.set_xlabel("Date")
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("No CME speed data available to plot.")
# ---------- UI ----------
st.title("🌞 Space Weather Dashboard")
st.write(f"Last update: {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
st.write("Recent CME Events")
st.dataframe(df[['Time', 'Speed', 'Note']].head(10), use_container_width=True)

# Plot
if "Speed" in df.columns and df["Speed"].notna().any():
    df_plot = df.dropna(subset=["Speed"]).copy()
    df_plot = df_plot.sort_values("Time")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_plot["Time"], df_plot["Speed"], marker='o', linestyle='-', color='#ff4444')
    ax.set_title("CME Speed (km/s)")
    ax.set_ylabel("Speed (km/s)")
    ax.set_xlabel("Date (UTC)")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No speed measurements available to plot.")
data = fetch_cme_data(days=7)

if not data:
    st.warning("No CME data returned.")
    st.stop()

df = pd.DataFrame(data)
df.columns = df.columns.astype(str).str.strip()
df.columns = df.columns.str.lower()  # normalize column names to lowercase
df = df.rename(columns={
    'time': 'time',
    'speed': 'speed',
    'note': 'note'
})
df['time'] = pd.to_datetime(df['time'], errors='coerce')  # ensure time is datetime
df['speed'] = pd.to_numeric(df['speed'], errors='coerce')  # ensure speed is numeric
def extract_speed_and_time(data):
    rows = []
    for item in data:
        time = item.get("startTime", "N/A")
        speed = None
        analyses = item.get("cmeAnalyses", [])
        if analyses and len(analyses) > 0:
            first_analysis = analyses[0]
            if isinstance(first_analysis, dict):
                speed = first_analysis.get("speed")
        rows.append({
            "Time": time,
            "Speed": speed,
            "Note": item.get("note", "No note")
        })
    df = pd.DataFrame(rows)
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df["Speed"] = pd.to_numeric(df["Speed"], errors="coerce")
    return df

df = extract_speed_and_time(data)
st.write(f"**CMEs in last 7 days:** {len(df)}")
st.dataframe(df.head(10))
print(df.columns)


# ---------- PLOT ----------

if "speed" in df.columns and df["speed"].notna().any():
    df_plot = df.dropna(subset=["speed"])
    df_plot["time"] = pd.to_datetime(df_plot["time"])
    df_plot = df_plot.sort_values("time")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_plot["time"], df_plot["speed"], marker="o")
    ax.set_title("CME Speed Over Last 7 Days (km/s)")
    ax.set_ylabel("Speed (km/s)")
    ax.set_xlabel("Date")
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("No CME speed data available.")

    if st.button("Refresh Now"):
        st.rerun()  # refreshes the whole page

# Auto-refresh every 10 minutes (600 seconds)
time.sleep(600)
st.rerun()