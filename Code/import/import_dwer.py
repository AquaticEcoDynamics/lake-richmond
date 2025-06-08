"""
Script: combine_water_levels_to_parquet.py

This script merges Excel files and safely saves them as a Parquet file,
cleaning non-numeric fields and avoiding Arrow type errors.
"""

import pandas as pd
from pathlib import Path

# --- Config ---
base_dir = Path("Data/data-lake/DWER")
file_names = ["WaterLevelsDiscreteForSiteFlatFile.xlsx", "WaterQualityDiscreteForSiteFlatFile.xlsx"]
output_path = "Data/data-warehouse/parquet/DWER/combined_water_levels.parquet"

# --- Locate files ---
xlsx_files = []
for name in file_names:
    xlsx_files.extend(base_dir.rglob(name))
print(f"🔍 Found {len(xlsx_files)} files.")

dfs = []

for file in xlsx_files:
    print(f"📄 Reading: {file}")
    df = pd.read_excel(file, engine='openpyxl')
    dfs.append(df)

# --- Combine ---
combined_df = pd.concat(dfs, ignore_index=True, sort=False)

# --- Load site coordinate data ---
site_info_path = "Code/governance/Full_Site_Listing - Public.xlsx"
site_df = pd.read_excel(site_info_path)

print("🧾 Columns in combined_df:", combined_df.columns.tolist())
print("🧾 Columns in site_df:", site_df.columns.tolist())


# Inspect available columns to find appropriate join key
if 'Site Ref' in combined_df.columns and 'Site Ref' in site_df.columns:
    print("🔗 Merging coordinates using 'Site Ref'...")
    coord_cols = ['Site Ref', 'Latitude', 'Longitude']
    site_df = site_df[coord_cols].drop_duplicates(subset=['Site Ref'])
    combined_df = combined_df.merge(site_df, on='Site Ref', how='left')

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


# --- Clean Reading Value ---
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

# --- Save as Parquet ---
combined_df.to_parquet(output_path, index=False, engine='pyarrow')
print(f"\n✅ Saved cleaned dataset to: {output_path}")