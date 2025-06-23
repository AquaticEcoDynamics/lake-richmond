

import pandas as pd
import os

"""
Script: import_hge_msc_level.py

Description:
    This script extracts digitised lake level data from two columns in the Excel sheet 'Picture 5',
    representing readings from the MSc board and MSc logger instruments. The data is labeled by source
    and appended to the existing consolidated lakelevel.parquet file for combined analysis.

Key Features:
    - Reads date/value pairs from columns J/K (MSc board) and N/O (MSc Logger)
    - Tags each dataset with agency and site metadata
    - Combines and appends to the central lakelevel.parquet repository
    - Handles NaN and type conversion for safe plotting and analysis

Inputs:
    - Excel File: Data/data-lake/HGE/MSc/HGE_DigitisedData.xlsx
    - Sheet: 'Picture 5'

Output:
    - Updated: Data/data-warehouse/parquet/level/lakelevel.parquet

Requirements:
    - pandas
    - openpyxl

Author: Brendan Busch
"""

# Configuration
excel_path = "Data/data-lake/HGE/MSc/HGE_DigitisedData.xlsx"
sheet_name = "Picture 5"

# Load columns J and K: MSc board
df_board = pd.read_excel(excel_path, sheet_name=sheet_name, usecols="J:K", names=["DateTime", "Reading"], header=None, skiprows=1)
df_board.dropna(inplace=True)
df_board["DateTime"] = pd.to_datetime(df_board["DateTime"], errors='coerce')
df_board["Reading"] = pd.to_numeric(df_board["Reading"], errors='coerce')
df_board.dropna(inplace=True)
df_board["Agency"] = "HGE"
df_board["Site"] = "Board (MSc)"
df_board["Variable"] = "Water Level (mAHD)"

# Load columns N and O: MSc Logger
df_logger = pd.read_excel(excel_path, sheet_name=sheet_name, usecols="N:O", names=["DateTime", "Reading"], header=None, skiprows=1)
df_logger.dropna(inplace=True)
df_logger["DateTime"] = pd.to_datetime(df_logger["DateTime"], errors='coerce')
df_logger["Reading"] = pd.to_numeric(df_logger["Reading"], errors='coerce')
df_logger.dropna(inplace=True)
df_logger["Agency"] = "HGE"
df_logger["Site"] = "Logger (MSc)"
df_logger["Variable"] = "Water Level (mAHD)"

# Combine both datasets
df_combined = pd.concat([df_board, df_logger], ignore_index=True)

# Reorder columns
df_combined = df_combined[["Agency", "Site", "DateTime", "Variable", "Reading"]]

# Load existing lakelevel.parquet
field_datapath = "Data/data-warehouse/parquet/level"
parquet_file = os.path.join(field_datapath, "lakelevel.parquet")
df_existing = pd.read_parquet(parquet_file)

# Append new data and save
updated_df = pd.concat([df_existing, df_combined], ignore_index=True)
updated_df.to_parquet(parquet_file, index=False)


print("HGE MSc board and logger data successfully appended to lakelevel.parquet")

# --- Plot appended data for visual inspection ---
import matplotlib.pyplot as plt

# Plot appended data only
fig, ax = plt.subplots(figsize=(10, 5))
for site, group in df_combined.groupby("Site"):
    ax.plot(group["DateTime"], group["Reading"], label=site, marker='o', linestyle='-')

ax.set_title("HGE MSc Sites - Lake Level (mAHD)")
ax.set_xlabel("Date")
ax.set_ylabel("Lake Level (mAHD)")
ax.legend()
plt.tight_layout()
plt.show()