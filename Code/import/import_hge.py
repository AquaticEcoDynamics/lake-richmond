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
df_logger["Site"] = "Logger"
df_logger["Variable"] = "Water Level (mAHD)"

# Reorder columns
df_logger = df_logger[["Agency", "Site", "DateTime", "Variable", "Reading"]]

# Define output path and parquet file
output_path = "Data/data-warehouse/parquet/level"
os.makedirs(output_path, exist_ok=True)
parquet_file = os.path.join(output_path, "lakelevel.parquet")

# Append to existing parquet file if it exists
if os.path.exists(parquet_file):
    existing_df = pd.read_parquet(parquet_file)
    combined_df = pd.concat([existing_df, df_logger], ignore_index=True)
else:
    combined_df = df_logger

combined_df.to_parquet(parquet_file, index=False)
print(f"Appended logger data to {parquet_file}")

# Plot the logger data
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(df_logger["DateTime"], df_logger["Reading"], color="green", label="HGE - Logger")
plt.xlabel("Date")
plt.ylabel("Water Level (mAHD)")
plt.title("HGE Logger Water Level Time Series")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()