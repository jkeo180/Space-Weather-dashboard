from skyfield.api import load, wgs84
import requests
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
response = requests.get(url) 
print("Status:", response.status_code) 
print("Text preview:", response.text[:300])