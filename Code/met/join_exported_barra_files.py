

"""
Script: join_exported_barra_files.py

Description:
    This script merges annual CSV files exported from BARRA NetCDF point extraction
    into a single CSV file. It removes duplicate time entries and sorts the data chronologically.

Requirements:
    - pandas
    - os

Author: Brendan Busch, Matthew Hipsey
"""

import os
import pandas as pd

# --- Directory containing the annual CSV files ---
input_dir = "Data/data-warehouse/csv/barra"
output_csv = "Data/data-warehouse/csv/barra_combined_timeseries.csv"

# --- Collect all CSV files ---
csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]

# --- Combine all files ---
df_list = []
for f in sorted(csv_files):
    full_path = os.path.join(input_dir, f)
    print(f"🔄 Loading {f}")
    df = pd.read_csv(full_path, parse_dates=["time"])
    df_list.append(df)

# --- Concatenate and deduplicate ---
combined_df = pd.concat(df_list, ignore_index=True)
combined_df = combined_df.drop_duplicates(subset=["time"])
combined_df = combined_df.sort_values(by="time")

# --- Export final CSV ---
combined_df.to_csv(output_csv, index=False)
print(f"✅ Combined CSV saved to: {output_csv}")