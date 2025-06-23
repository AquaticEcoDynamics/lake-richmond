"""
Script: import_360e_logger_data.py

Description:
    Imports environmental monitoring data from the 'Data Logger' sheet of the 360 Environmental Excel file
    and writes each variable to a separate Parquet file for further use in the Lake Richmond data platform.

Key Features:
    - Extracts and reshapes data from the 'Data Logger' worksheet
    - Uses a variable renaming dictionary to standardize field names
    - Appends metadata fields: Agency = '360E', Site = 'Depth Board'
    - Saves each variable as an individual Parquet file

Output:
    Parquet files saved to Data/data-warehouse/parquet/logger/

Requirements:
    - pandas
    - pyarrow

Author: Brendan Busch
"""

import os
import pandas as pd
from pathlib import Path

# Configuration
excel_file = "Data/data-lake/360E/4713AA_Rev 2 Lake Richmond Monitoring field & lab data.xlsx"
sheet_name = "Data Logger"
output_dir = "Data/data-warehouse/parquet/WQ"
os.makedirs(output_dir, exist_ok=True)

# Variable standardisation dictionary
variable_map = {
    "pH (pH units)": ("pH", "pH"),
    "Specific Conductivity (uS/cm)": ("Specific Conductivity  (uS/cm)", "Specific_Conductivity"),
    "Temperature (DegC)": ("Temperature (C)", "Temperature"),
    "Dissolved Oxygen (mg/L)": ("DO (mg/L)", "DO_mgL"),
    "Dissolved Oxygen Saturation (%)": ("DO (%)", "DO_percent"),
    "Pressure (HPa)": ("Pressure (HPa)", "Pressure"),
    "Measured Conductivity (µS/cm)": ("Electrical Conductivity (µS/cm)", "Electrical_Conductivity"),
    "Temperature (°C)": ("Temperature (C)", "Temperature"),
    "TDS (mg/L)": ("TDS (mg/L)", "TDS"),
    "Measured Salinity (PSU)": ("Salinity (PSU)", "Salinity")
}

# Read the data logger sheet
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# Ensure datetime is parsed properly
df["DateTime"] = pd.to_datetime(df["Date"])

# Loop through variable columns and export each
for original_var, (standard_var, clean_name) in variable_map.items():
    if original_var not in df.columns:
        continue

    df_out = df[["DateTime", original_var]].copy()
    df_out = df_out.rename(columns={original_var: "Reading"})
    df_out = df_out.dropna(subset=["Reading"])
    df_out["Agency"] = "360E"
    df_out["Site"] = "Board (2022)"
    df_out["Variable"] = standard_var

    # Save as Parquet
    output_file = Path(output_dir) / f"{clean_name}.parquet"
    df_out.to_parquet(output_file, index=False)
    print(f"Saved: {output_file}")