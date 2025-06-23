# Import necessary libraries 
import os
import pandas as pd
import matplotlib.pyplot as plt

# Re-define the file path after reset
excel_file = "Data/data-lake/MWH/MWH_DigitisedData.xlsx"

# Load the Excel file and the first sheet
xls_new = pd.ExcelFile(excel_file)
df_level = pd.read_excel(xls_new, sheet_name=0)

# Display the first few rows
df_level.head()

# Prepare both datetime series and corresponding elevation data
df_level['Datetime_1'] = pd.to_datetime(df_level['date'], errors='coerce')
df_level['Datetime_2'] = pd.to_datetime(df_level['date.1'], errors='coerce')

# Filter and prepare two data series for plotting
df1 = df_level[['Datetime_1', 'Stadia WL']].dropna()
df2 = df_level[['Datetime_2', 'WL Elevation']].dropna()

# Plot both time series
plt.figure(figsize=(12, 6))
plt.plot(df1['Datetime_1'], df1['Stadia WL'], label='Stadia WL', color='orange', marker='o', linestyle='None')
plt.plot(df2['Datetime_2'], df2['WL Elevation'], label='WL Elevation', color='blue', marker='x')
plt.xlabel("Date")
plt.ylabel("Water Level (m AHD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# plt.show()

plt.savefig('Data/data-lake/MWH/MWH_WL.png')

# Prepare and append Stadia WL data
stadia_df = pd.DataFrame({
    "Agency": "MWH",
    "Site": "Board",
    "DateTime": df1["Datetime_1"],
    "Variable": "Water Level (mAHD)",
    "Reading": df1["Stadia WL"]
})

# Prepare and append WL Elevation data
wl_df = pd.DataFrame({
    "Agency": "MWH",
    "Site": "Logger",
    "DateTime": df2["Datetime_2"],
    "Variable": "Water Level (mAHD)",
    "Reading": df2["WL Elevation"]
})

# Combine and save to Parquet
combined_df = pd.concat([stadia_df, wl_df], ignore_index=True)

datapath = "Data/data-warehouse/parquet/level"
os.makedirs(datapath, exist_ok=True)
parquet_file = os.path.join(datapath, "lakelevel.parquet")

if os.path.exists(parquet_file):
    existing_df = pd.read_parquet(parquet_file)
    combined_df = pd.concat([existing_df, combined_df], ignore_index=True)

combined_df.to_parquet(parquet_file, index=False)
print(f"Appended data to {parquet_file}")

# Load and summarize site information from the Parquet file
df = pd.read_parquet(parquet_file)

# Display all unique sites
unique_sites = df["Site"].unique()
print("Sites in the dataset:", unique_sites)

# Display the number of records per site
print("Record count per site:")
print(df["Site"].value_counts())
