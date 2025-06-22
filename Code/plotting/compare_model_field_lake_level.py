"""
Script: compare_model_field_lake_level.py

Description:
    This script compares modeled lake level outputs against observed field data from various sources.
    It loads data from a Parquet archive and a CSV file, harmonizes their formats, and produces a
    customizable time series plot for visual comparison.

Key Features:
    - Loads and cleans model output from lake.csv
    - Imports and integrates historical field measurements
    - Applies customizable styles per site and agency
    - Handles edge cases like '24:00:00' timestamps
    - Displays combined time series for visual validation

Inputs:
    - Field data: Data/data-warehouse/parquet/level/lakelevel.parquet
    - Model data: Model/richmond/output/lake.csv

Output:
    - Interactive matplotlib time series plot comparing field and model lake levels

Configuration:
    - xlim_start / xlim_end: control plot window
    - plot_styles: define color and plot type per site
    - xtickint: controls tick frequency on x-axis

Requirements:
    - pandas
    - matplotlib
    - Python 3.7+

Author: Brendan Busch
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# -------------------- Configuration Section --------------------

# Plot x-axis limits - customize these to zoom in/out on specific periods
xlim_start = pd.Timestamp("2010-01-01")
xlim_end = pd.Timestamp("2020-01-01")

# Plot styles by site - customize marker types and colors for each site
plot_styles = {
    "s6142501": {"kind": "scatter", "color": "blue"},
    "Stadia": {"kind": "scatter", "color": "orange"},
    "WL": {"kind": "scatter", "color": "black"},
    "Logger": {"kind": "scatter", "color": "green"},
    "Grab": {"kind": "scatter", "color": "pink"},
    "MSc board": {"kind": "scatter", "color": "purple"},
    "MSc Logger": {"kind": "scatter", "color": "brown"},
    "Board": {"kind": "scatter", "color": "cyan"},
    "Model": {"kind": "line", "color": "red"},
    
}

# Interval for X Ticks (yearly) - adjust for more or fewer ticks on x-axis
xtickint = 1

# Model file path
model_file = "Model/richmond/output/lake.csv"


# -------------------- Data Loading Section --------------------

# Load field data from Parquet file
field_datapath = "Data/data-warehouse/parquet/level"
parquet_file = os.path.join(field_datapath, "lakelevel.parquet")
df_field = pd.read_parquet(parquet_file)

# Load model data from CSV file
df_model = pd.read_csv(model_file)

print(df_model.columns)

# -------------------- Data Processing Section --------------------

# Replace '24:00:00' with '00:00:00' and add 1 day to handle midnight edge case
df_model["time"] = df_model["time"].str.replace("24:00:00", "00:00:00")
df_model["DateTime"] = pd.to_datetime(df_model["time"], errors='coerce') + pd.to_timedelta(df_model["time"].str.contains("24:00:00").astype(int), unit='D')

# Add metadata columns for consistency with field data
df_model["Site"] = "Model"
df_model["Agency"] = "Model"
df_model["Variable"] = "Water Level (mAHD)"
df_model["Reading"] = df_model["Lake Level"] - 14.6

# Select relevant columns for plotting
df_model = df_model[["Agency", "Site", "DateTime", "Variable", "Reading"]]

# -------------------- Data Combination --------------------

# Combine field and model data into a single DataFrame
df = pd.concat([df_field, df_model], ignore_index=True)

# Display all unique sites in the combined dataset
unique_sites = df["Site"].unique()
print("Sites in the dataset:", unique_sites)

# -------------------- Plotting Section --------------------

# Create the plot figure with specified size
plt.figure(figsize=(12, 6))

# Plot each site separately with its designated style
for site in df["Site"].unique():
    site_df = df[df["Site"] == site]
    label = f"{site_df['Agency'].iloc[0]} - {site}"
    style = plot_styles.get(site, {"kind": "line", "color": "gray"})
    if style["kind"] == "line":
        plt.plot(site_df["DateTime"], site_df["Reading"], label=label, color=style["color"])
    elif style["kind"] == "scatter":
        plt.scatter(site_df["DateTime"], site_df["Reading"], label=label, color=style["color"], s=10)

# Set axis labels and title
plt.xlabel("Year")
plt.ylabel("Water Level (mAHD)")
plt.title("Lake Level Time Series: Model vs Field Data")
plt.grid(True)

# Configure x-axis ticks and formatting
locator = mdates.YearLocator(xtickint)
formatter = mdates.DateFormatter('%Y')
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)

# Set x-axis limits according to configuration
plt.xlim(xlim_start, xlim_end)

# Add legend and adjust layout
plt.legend()
plt.tight_layout()

# Show the plot
plt.show()
