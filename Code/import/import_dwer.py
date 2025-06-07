"""
Script: combine_water_levels_to_parquet.py

This script merges Excel files and safely saves them as a Parquet file,
cleaning non-numeric fields and avoiding Arrow type errors.
"""

import pandas as pd
from pathlib import Path

# --- Config ---
base_dir = Path("Data/data-lake/DWER")
file_name = "WaterLevelsDiscreteForSiteFlatFile.xlsx"
output_path = "Data/data-warehouse/parquet/DWER/combined_water_levels.parquet"

# --- Locate files ---
xlsx_files = list(base_dir.rglob(file_name))
print(f"🔍 Found {len(xlsx_files)} files.")

dfs = []

for file in xlsx_files:
    print(f"📄 Reading: {file}")
    df = pd.read_excel(file, engine='openpyxl')
    dfs.append(df)

# --- Combine ---
combined_df = pd.concat(dfs, ignore_index=True, sort=False)

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