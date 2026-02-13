import requests
from datetime import datetime, timedelta, timezone
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from os import getenv
from dotenv import load_dotenv

load_dotenv()
API_KEY = getenv("NASA_API_KEY")

if not API_KEY:
    st.error("NASA API key not found. Please set it in the .env file.")
    st.stop()

def fetch_cme_data(days=7):
    base_url = "https://api.nasa.gov/DONKI/CME"
    
    now = datetime.now(timezone.utc)
    end_date = now.strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "api_key": API_KEY.strip()
    }

    print("DEBUG: API_KEY:", API_KEY if API_KEY else "MISSING!")
    print("DEBUG: Full URL:", base_url + "?" + "&".join(f"{k}={v}" for k,v in params.items()))

    try:
        response = requests.get(base_url, params=params, timeout=10)
        print("DEBUG: Status:", response.status_code)
        print("DEBUG: Headers:", response.headers)
        response.raise_for_status()
        data = response.json()
        print("DEBUG: Data length:", len(data))
        return data
    except requests.exceptions.HTTPError as e:
        print("DEBUG: HTTP Error:", e.response.status_code, e.response.text)
        st.error(f"API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print("DEBUG: Other error:", str(e))
        st.error(f"Request failed: {str(e)}")
        return []

def extract_speed_and_time(data):
    rows = []
    for item in data:
        time_str = item.get("startTime", "N/A")
        speed = None
        analyses = item.get("cmeAnalyses", [])
        if analyses and len(analyses) > 0:
            first = analyses[0]
            if isinstance(first, dict):
                speed = first.get("speed")
        rows.append({
            "Time": time_str,
            "Speed": speed,
            "Note": item.get("note", "")
        })
        return pd.DataFrame(rows) 
    df = pd.DataFrame(rows)
    #df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce")
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df["Speed"] = pd.to_numeric(df["Speed"], errors="coerce")
    return df

st.set_page_config(page_title="Space Weather Dashboard", layout="wide")

st.title("Real-Time Space Weather Dashboard") 
st.write(f"Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}") 

data = fetch_cme_data(days=7)

if not data:
    st.error("No raw data from NASA API — check your API key or connection.") 
    st.stop()

df = extract_speed_and_time(data)
df = pd.json_normalize(data, record_path=['cmeAnalyses'], meta=['startTime'])
if df.empty:
    st.warning("No CMEs detected in the last 7 days.")
    st.stop()

# Display
col1, col2 = st.columns(2)
col1.metric("CMEs Detected (7 Days)", len(df))

st.write("Recent CME Events")
df_display = extract_speed_and_time(data)

# 2. Select the columns (only if the dataframe isn't empty)
if not df_display.empty:
    filtered_df = df_display[['Time', 'Speed', 'Note']].head(10)
    # 3. Pass to streamlit (Note: no 'df=' inside the parenthesis)
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("No CME data found.")

# Plot
st.subheader("CME Speed Trend")
if "Speed" in df.columns and df["Speed"].notna().any():
    df_plot = df.dropna(subset=["Speed"]).copy()
    df_plot = df_plot.sort_values("Time")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_plot["Time"], df_plot["Speed"], marker='o', linestyle='-', color='#ff4444')
    ax.set_title("CME Speed (km/s)", fontsize=16)
    ax.set_ylabel("Speed (km/s)")
    ax.set_xlabel("Date (UTC)")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No speed measurements available to plot.")

if st.button("Refresh Now"):
    st.rerun()