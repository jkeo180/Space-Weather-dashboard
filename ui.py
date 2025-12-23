from skyfield.api import load, EarthSatellite, wgs84
import streamlit as st
import requests
from io import StringIO
import pandas as pd
import time

st.title("Live Satellite Tracker — Active Satellites")

url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
@st.cache_resource
def load_satellites(ttl=3600, show_spinner="Downloading TLE data..."):
    with st.spinner(show_spinner):
        response = requests.get(url)
        response.raise_for_status() 
        lines = response.text.strip().splitlines()
        ts = load.timescale()
        satellites = []
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                name = lines[i].strip()
                line1 = lines[i+1].strip()
                line2 = lines[i+2].strip()
                
                try: 
                    ts = load.timescale() # it's already a thing in Skyfield 
                    sat = EarthSatellite(line1, line2, name, ts)
                    satellites.append((name, sat))
                    if len(satellites) >= 10:  # limit to 10 for speed
                        break
                except ValueError:
                    pass
    return ts, satellites
ts, satellites = load_satellites()

placeholder = st.empty()
status = st.empty()

while True:
    now = ts.now()
    data = []
    for name, sat in satellites:
        geocentric = sat.at(now)
        subpoint = wgs84.subpoint(geocentric)
        data.append({
            "name": name,
            "lat": round(subpoint.latitude.degrees, 4),
            "lon": round(subpoint.longitude.degrees, 4),
            "alt_km": round(subpoint.elevation.km)
        })
    time.sleep(10) # throttle
    df = pd.DataFrame(data) 
    if len(df) == 0: 
        st.warning("No satellites loaded — check URL") 
        time.sleep(5)
        continue
    df = pd.DataFrame(data)
    
    with placeholder.container():
        st.map(df, latitude="lat", longitude="lon", size=100, color="#ff0000")
        st.dataframe(df)
    
    status.write(f"Last update: {now.utc_strftime('%H:%M:%S UTC')} — refreshing in 10s")
    time.sleep(10)