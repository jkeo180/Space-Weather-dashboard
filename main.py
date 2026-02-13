import requests
from skyfield.api import load, EarthSatellite, wgs84
import time
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from subprocess import Popen

st.write("Loading TLE data from Celestrak...")
ctx = get_script_run_ctx()
headers = {'User-Agent': 'Mozilla/5.0'}
# Update TLE data source to include both active satellites and stations     
# 1. All active sats
r1 = requests.get("https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle", headers=headers).text

# 2. Just in case something is missing, grab stations.txt too (has ISS nice name)
r2 = requests.get("https://celestrak.org/NORAD/elements/stations.txt", headers=headers).text

# Merge them - just concatenate the text, the parsing logic will handle lines
full_text = r1 + r2

ts = load.timescale()
now = ts.now()

satellites = []
# Correctly parse TLE data from full_text by splitting lines and grouping by 3
lines = full_text.strip().splitlines()
for i in range(0, len(lines), 3):
    if i + 2 < len(lines): # Ensure there are 3 lines for a TLE block
        name = lines[i].strip()
        line1 = lines[i+1].strip()
        line2 = lines[i+2].strip()
        try:
            sat = EarthSatellite(line1, line2, name, ts)
            satellites.append((name, sat))
        except ValueError as e:
            pass # Suppress errors for malformed TLEs

print(f"Total satellites loaded: {len(satellites)}")

print("First 10 names:")
for name, _ in satellites[:10]: # Print names from the created list
    print("  ", name)

# Example: print current position of first 5
print("\nLive positions (lat, lon, alt km) for first 5 satellites: ")
for name, sat in satellites[:5]:
    try:
        geo = sat.at(now)
        subpoint = wgs84.subpoint(geo)
        print(f"{name:30}  {subpoint.latitude.degrees:7.3f}°  {subpoint.longitude.degrees:8.3f}°  {subpoint.elevation.km:6.1f} km")
    except Exception as e:
        print(f"Error calculating position for {name}: {e}")
process = Popen(['python', 'my_script.py'])
add_script_run_ctx(process, ctx)