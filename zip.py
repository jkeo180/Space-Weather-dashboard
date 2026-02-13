import zipfile
import pandas as pd

# Open the zip file
with zipfile.ZipFile('your_archive.zip', 'r') as zf:
    # Create a list to hold dataframes from each CSV
    csv_dataframes = []
    for name in zf.namelist():
        if name.endswith('.csv'):
            # Open and read each CSV into a pandas DataFrame
            # Use zf.open(name) to read from memory
            csv_dataframes.append(pd.read_csv(zf.open(name), header=None)) # header=None if no headers

    # Concatenate all dataframes into one and save to a new CSV
    combined_df = pd.concat(csv_dataframes, ignore_index=True)
    combined_df.to_csv('combined_output.csv', index=False, header=False) # index=False to skip index
    print("CSV files have been combined into 'combined_output.csv'")