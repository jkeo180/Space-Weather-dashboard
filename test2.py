from main import fetch_cme_data, extract_speed_and_time

data = fetch_cme_data(days=7)
print("Raw data length:", len(data) if data else "None/Empty")
df = extract_speed_and_time(data)
print("DF columns:", df.columns.tolist())
print("DF shape:", df.shape)
print(df.head())