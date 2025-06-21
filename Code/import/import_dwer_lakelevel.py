import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

datapath = "Data/data-lake/DWER/174756"
# Load the Excel file
file_name = "WaterLevelsDiscreteForSiteFlatFile.xlsx"

file_path = os.path.join(datapath, file_name)
df = pd.read_excel(file_path, sheet_name="WaterLevelsDiscreteForSiteFlatF")

# Convert 'Collected Date Time' to datetime format and store in a new column 'DateTime'
df["DateTime"] = pd.to_datetime(df["Collected Date Time"])

# Clean the 'Reading Value' column to ensure it's numeric
df["Reading Value"] = (
    df["Reading Value"]
    .astype(str)
    .str.replace(r"[<>~]", "", regex=True)  # Remove '<', '>', '~'
    .str.strip()
    .astype(float)
)

# Adjust 'Reading Value' where 'Variable Name' is "Storage level (AHD) (m)"
df.loc[df["Variable Name"] == "Storage level (SLE) (m)", "Reading Value"] -= 97

# Show the first few rows to verify
print(df.head())

# Create a simple time series plot
plt.figure(figsize=(12, 6))
plt.plot(df["DateTime"], df["Reading Value"], label="Water Level (mAHD)")

# Set axis labels
plt.xlabel("Year")
plt.ylabel("Lake Level")
plt.title("Lake Level Over Time")

# Set x-axis major ticks every 10 years
locator = mdates.YearLocator(10)
formatter = mdates.DateFormatter('%Y')
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)
plt.xlim(pd.Timestamp("1940-01-01"), pd.Timestamp("2020-01-01"))

plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

# Prepare a reduced DataFrame for export
export_df = pd.DataFrame({
    "Agency": "DWER",
    "Site": "s6142501",
    "DateTime": df["DateTime"],
    "Variable": "Water Level (mAHD)",
    "Reading": df["Reading Value"]
})

# Save to Parquet

parquet_path = "Data/data-warehouse/parquet/level"
os.makedirs(parquet_path, exist_ok=True)

output_parquet_path = os.path.join(parquet_path, "lakelevel.parquet")
export_df.to_parquet(output_parquet_path, index=False)
print(f"Exported to {output_parquet_path}")
