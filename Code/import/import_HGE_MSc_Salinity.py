"""
Script: import_HGE_MSc_Salinity.py

Description:
    This script imports salinity data from the 'Picture 1' sheet of the HGE_DigitisedData.xlsx file.
    The raw salinity data (mg/L) is converted to PSU and appended to an existing Parquet file
    used for salinity data analysis.

Key Features:
    - Reads salinity values from specified columns in an Excel sheet
    - Converts mg/L salinity to PSU using an approximate conversion factor
    - Appends standardized data to a structured Parquet dataset

Output:
    Updated salinity.parquet file in Data/data-warehouse/parquet/WQ/

Requirements:
    - pandas
    - openpyxl
    - pyarrow

Author: Brendan Busch
"""

import pandas as pd
import os

# File and sheet details
excel_path = "Data/data-lake/HGE/MSc/HGE_DigitisedData.xlsx"
sheet_name = "Picture 1"

# Load the salinity data
df = pd.read_excel(excel_path, sheet_name=sheet_name, usecols="O:P", skiprows=2, names=["DateTime", "Salinity_mg_L"])
df = df.dropna(subset=["DateTime", "Salinity_mg_L"])

# Convert salinity from mg/L to PSU using a freshwater-appropriate conversion factor.
# This factor (0.000806) better reflects salinity behavior in low-conductivity environments,
# such as Lake Richmond, compared to the rough seawater approximation of 1 PSU ≈ 1000 mg/L.
df["Salinity_PSU"] = df["Salinity_mg_L"] * 0.000806


# Create output DataFrame
df_out = pd.DataFrame({
    "Agency": "HGE",
    "Site": "MSc Logger",
    "DateTime": pd.to_datetime(df["DateTime"]),
    "Variable": "Salinity (PSU)",
    "Reading": df["Salinity_PSU"]
})

# Define output path
output_path = "Data/data-warehouse/parquet/WQ/salinity.parquet"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Append or create the parquet file
if os.path.exists(output_path):
    df_existing = pd.read_parquet(output_path)
    df_combined = pd.concat([df_existing, df_out], ignore_index=True)
else:
    df_combined = df_out

# Save to Parquet
df_combined.to_parquet(output_path, index=False)
print(f"Appended salinity data to {output_path}")


# --- Import and append TDS data from "Picture 5" sheet ---

# Load the TDS data
df_tds = pd.read_excel(excel_path, sheet_name="Picture 5", usecols="AD:AE", skiprows=2, names=["DateTime", "TDS_mg_L"])
df_tds = df_tds.dropna(subset=["DateTime", "TDS_mg_L"])

# Display the first few rows of the TDS DataFrame for verification
print(df_tds.head())

# Create output DataFrame
df_tds_out = pd.DataFrame({
    "Agency": "HGE",
    "Site": "MSc Logger",
    "DateTime": pd.to_datetime(df_tds["DateTime"]),
    "Variable": "TDS (mg/L)",
    "Reading": df_tds["TDS_mg_L"]
})

# Define output path
tds_output_path = "Data/data-warehouse/parquet/WQ/tds.parquet"

# Ensure output directory exists
os.makedirs(os.path.dirname(tds_output_path), exist_ok=True)

# Append or create the parquet file
if os.path.exists(tds_output_path):
    df_existing_tds = pd.read_parquet(tds_output_path)
    df_combined_tds = pd.concat([df_existing_tds, df_tds_out], ignore_index=True)
else:
    df_combined_tds = df_tds_out

# Save to Parquet
df_combined_tds.to_parquet(tds_output_path, index=False)
print(f"Appended TDS data to {tds_output_path}")