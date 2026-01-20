import pandas as pd

from main import extract_speed_and_time
# Test with fake data
test_data = [
    {"startTime": "2025-01-01T12:00Z", "cmeAnalyses": [{"speed": 500}]},
    {"startTime": "2025-01-02T14:00Z", "cmeAnalyses": []},
    {"startTime": "2025-01-03T16:00Z", "cmeAnalyses": [None]},
    {"startTime": "2025-01-04T18:00Z"}  # missing key
]   
df = extract_speed_and_time(test_data)
print(df)