"""
Script: import_dwer.py

Description:
    This script ingests discrete water level and water quality data from DWER Excel exports,
    merges them into a single DataFrame, attaches site coordinate metadata, cleans key fields,
    and exports the results to a Parquet file for further analysis.

Key Features:
    - Supports multiple input file types (e.g., WaterLevelsDiscreteForSiteFlatFile.xlsx, WaterQualityDiscreteForSiteFlatFile.xlsx)
    - Automatically finds all matching files in nested directories
    - Merges site metadata from a master listing file
    - Handles type cleaning and conversion for numeric fields
    - Logs processing duration and flags missing site coordinates

Output:
    Parquet file saved to Data/data-warehouse/parquet/DWER/combined_water_levels.parquet

Requirements:
    - pandas
    - openpyxl
    - pyarrow

Author: Brendan Busch, Matthew Hipsey


""" 

import pandas as pd
from pathlib import Path
import time

# --- Config ---
# List of expected file patterns to process (add more if needed)
base_dir = Path("Data/data-lake/DWER")
file_names = ["WaterLevelsDiscreteForSiteFlatFile.xlsx", "WaterQualityDiscreteForSiteFlatFile.xlsx"]
output_path = "Data/data-warehouse/parquet/DWER/combined_water_levels.parquet"

# Recursively search for all matching Excel files
xlsx_files = []
for name in file_names:
    xlsx_files.extend(base_dir.rglob(name))
print(f"🔍 Found {len(xlsx_files)} files.")

dfs = []

start_time = time.time()

for file in xlsx_files:
    print(f"📄 Reading: {file}")
    t0 = time.time()
    df = pd.read_excel(file, engine='openpyxl')
    print(f"⏱️ Read completed in {time.time() - t0:.2f} seconds")
    # Append loaded DataFrame to the list
    dfs.append(df)

# Combine all individual Excel DataFrames into one
combined_df = pd.concat(dfs, ignore_index=True, sort=False)
print(f"🧬 Combined dataframe shape: {combined_df.shape}")

# Load site metadata containing Latitude/Longitude
site_info_path = "Code/governance/Full_Site_Listing - Public.xlsx"
site_df = pd.read_excel(site_info_path)

print("🧾 Columns in combined_df:", combined_df.columns.tolist())
print("🧾 Columns in site_df:", site_df.columns.tolist())


# Perform coordinate merge using 'Site Ref' as the join key
if 'Site Ref' in combined_df.columns and 'Site Ref' in site_df.columns:
    print("🔗 Merging coordinates using 'Site Ref'...")
    coord_cols = ['Site Ref', 'Latitude', 'Longitude']
    site_df = site_df[coord_cols].drop_duplicates(subset=['Site Ref'])
    combined_df = combined_df.merge(site_df, on='Site Ref', how='left')
    print(f"📌 After coordinate merge: {combined_df.shape}")

    # --- Check for missing sites ---
    missing_sites = combined_df[combined_df['Latitude'].isna() & combined_df['Longitude'].isna()]
    if not missing_sites.empty:
        unique_missing = missing_sites['Site Ref'].dropna().unique()
        print(f"⚠️ {len(unique_missing)} site(s) missing coordinate data:")
        print(unique_missing)
    else:
        print("✅ All sites matched with coordinates.")
else:
    print("⚠️ 'Site Ref' column missing in one of the datasets. Skipping coordinate merge.")


# Normalize and sanitize the 'Reading Value' column for numeric conversion
if 'Reading Value' in combined_df.columns:
    print("🧼 Cleaning 'Reading Value' column...")
    # Rename original to make it safe
    combined_df['Reading Value (Raw)'] = combined_df['Reading Value'].astype(str)

    # Create a cleaned numeric version
    combined_df['Reading Value (Clean)'] = (
        combined_df['Reading Value (Raw)']
        .str.replace(r'[<>]', '', regex=True)
        .str.strip()
    )

    combined_df['Reading Value (Clean)'] = pd.to_numeric(
        combined_df['Reading Value (Clean)'], errors='coerce'
    )

    # Overwrite original column with safe string version for Parquet
    combined_df['Reading Value'] = combined_df['Reading Value (Raw)']
    print(f"🔢 Finished cleaning 'Reading Value' column.")

# --- Convert 'Sample Depths M' to numeric if present ---
if 'Sample Depths M' in combined_df.columns:
    print("🔧 Converting 'Sample Depths M' to numeric...")
    combined_df['Sample Depths M'] = pd.to_numeric(combined_df['Sample Depths M'], errors='coerce')

# --- Convert 'COC No' to string to avoid ArrowTypeError ---
if 'COC No' in combined_df.columns:
    print("🔧 Converting 'COC No' to string...")
    combined_df['COC No'] = combined_df['COC No'].astype(str)

# --- Remove rows with NaN Reading Value ---
pre_drop_shape = combined_df.shape
combined_df = combined_df.dropna(subset=['Reading Value'])
print(f"🧹 Removed {pre_drop_shape[0] - combined_df.shape[0]} rows with NaN Reading Value.")

# Export the final DataFrame to a Parquet file using pyarrow
combined_df.to_parquet(output_path, index=False, engine='pyarrow')
print(f"\n✅ Saved cleaned dataset to: {output_path}")
print(f"⏳ Total runtime: {time.time() - start_time:.2f} seconds")