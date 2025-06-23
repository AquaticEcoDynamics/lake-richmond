import pandas as pd
import os

# Load Excel file
logger_file = "Data/data-lake/HGE/2018/Copy of Richmond 01.xlsx"
xls = pd.ExcelFile(logger_file)

# Parse the relevant sheet
df_logger = xls.parse("Final Logger mAHD Data")

# Rename columns and clean data
df_logger = df_logger.rename(columns={"Date/time": "DateTime", "resovled data mAHD": "Reading"})
df_logger["DateTime"] = pd.to_datetime(df_logger["DateTime"])
df_logger["Agency"] = "HGE"
df_logger["Site"] = "Logger (2018)"
df_logger["Variable"] = "Water Level (mAHD)"

# Reorder columns
df_logger = df_logger[["Agency", "Site", "DateTime", "Variable", "Reading"]]

# Append to existing parquet file if it exists
output_path = "Data/data-warehouse/parquet/level"
os.makedirs(output_path, exist_ok=True)
parquet_file = os.path.join(output_path, "lakelevel.parquet")

if os.path.exists(parquet_file):
    existing_df = pd.read_parquet(parquet_file)
    df_combined = pd.concat([existing_df, df_logger], ignore_index=True)
else:
    df_combined = df_logger

# Extract Grab dataset from 'Point Hydro Data' sheet
df_grab = xls.parse("Point Hydro Data")
df_grab = df_grab.rename(columns={df_grab.columns[0]: "DateTime", df_grab.columns[13]: "Reading"})  # Column A and N
df_grab["DateTime"] = pd.to_datetime(df_grab["DateTime"], errors="coerce")
df_grab["Reading"] = pd.to_numeric(df_grab["Reading"], errors="coerce")
df_grab.dropna(subset=["DateTime", "Reading"], inplace=True)
df_grab["Agency"] = "HGE"
df_grab["Site"] = "Board (2018)"
df_grab["Variable"] = "Water Level (mAHD)"
df_grab = df_grab[["Agency", "Site", "DateTime", "Variable", "Reading"]]

# Append to existing combined dataframe
df_combined = pd.concat([df_combined, df_grab], ignore_index=True)

df_combined.to_parquet(parquet_file, index=False)
print(f"Appended logger data to {parquet_file}")

# Plot the logger data
import matplotlib.pyplot as plt

# plt.figure(figsize=(12, 6))
# plt.plot(df_combined[df_combined["Site"] == "Logger (2018)"]["DateTime"], df_combined[df_combined["Site"] == "Logger"]["Reading"], color="green", label="HGE - Logger")
# plt.plot(df_combined[df_combined["Site"] == "Board (2018)"]["DateTime"], df_combined[df_combined["Site"] == "Grab"]["Reading"], color="blue", label="HGE - Grab")
# plt.xlabel("Date")
# plt.ylabel("Water Level (mAHD)")
# plt.title("HGE Logger Water Level Time Series")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()