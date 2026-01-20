import requests
from datetime import datetime, timedelta,timezone
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from os import getenv
from dotenv import load_dotenv

# ---------- ENV ----------
load_dotenv()
API_KEY = getenv("NASA_API_KEY")

if not API_KEY:
    st.error("NASA API key not found. Please set it in the .env file.")
    st.stop()

# ---------- DATA FETCH ----------
def fetch_cme_data(days=7):
    url = "https://api.nasa.gov/DONKI/CME"
    now_aware = datetime.now(timezone.utc)
    end_date = now_aware
    start_date = end_date - timedelta(days=days)

    params = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "startTime": "00:00",
        "endTime": "23:59",
        "cmeAnalysis": "true",
        "speed": "true",
        "note": "true",
        "api_key": API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return []
# ---------- TRANSFORM ----------
def extract_speed_and_time(data):
    rows = []    
    for item in data:
        # Safe extraction
        time = item.get("startTime")
        analyses = item.get("cmeAnalyses", [])
        
        # Get speed from FIRST analysis ONLY IF it exists and is a dict
        speed = None
        if analyses and isinstance(analyses[0], dict):
            speed = analyses[0].get("speed")
        
        rows.append({
            "time": time,
            "speed": speed,
            "note": item.get("note", "")
        })
    
    df = pd.DataFrame(rows)
    return df
# ---------- UI ----------
st.title("🌞 Space Weather Dashboard")
st.write(f"Last update: {datetime.now(timezone.utc).strftime('%H:%M UTC')}")

data = fetch_cme_data(days=7)

if not data:
    st.warning("No CME data returned.")
    st.stop()
df = pd.DataFrame(data)
df.columns = df.columns.astype(str).str.strip()
df = extract_speed_and_time(data)
st.write(f"**CMEs in last 7 days:** {len(df)}")
st.dataframe(df.head(10))

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

