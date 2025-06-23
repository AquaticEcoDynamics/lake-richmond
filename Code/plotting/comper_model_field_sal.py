"""
Script: compare_model_field_temp.py

Description:
    This script compares modeled lake temperature outputs against observed field data from various sources.
    It loads data from a Parquet archive and a CSV file, harmonizes their formats, and produces a
    customizable time series plot for visual comparison.

Key Features:
    - Loads and cleans model output from WQ_1.csv
    - Imports and integrates historical field temperature measurements
    - Applies customizable styles per site and agency
    - Handles edge cases like '24:00:00' timestamps
    - Displays combined time series for visual validation

Inputs:
    - Field data: Data/data-warehouse/parquet/WQ/Temperature.parquet
    - Model data: Model/richmond/output/WQ_1.csv

Output:
    - Interactive matplotlib time series plot comparing field and model temperatures

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
from matplotlib.ticker import MultipleLocator
import numpy as np

# Configuration
xlim_start = pd.to_datetime("2010-01-01")
xlim_end = pd.to_datetime("2025-12-31")
xtickint = 12  # months

plot_styles = {
    "Model": {
        "kind": "line",
        "color": "red",
        "linestyle": "-",
        "marker": None,
        "label": "Model"
    },
    "Depth Board": {
        "kind": "scatter",
        "color": "blue",
        "linestyle": "",
        "marker": "o",
        "label": "360E - Depth Board"
    },
    "MSc Logger": {
        "kind": "scatter",
        "color": "orange",
        "linestyle": "",
        "marker": "s",
        "label": "HGE - Logger"
    }
}

# Load model data
model_fp = "Model/richmond/output/WQ_1.csv"
model_df = pd.read_csv(model_fp)

# Handle timestamps with hours > 23 (e.g. 25:00:00) by splitting and adding timedelta
def parse_model_time(ts):
    date_part, time_part = ts.strip().split(" ")
    hour, minute, second = map(int, time_part.split(":"))
    base_time = pd.to_datetime(date_part)
    return base_time + pd.to_timedelta(hour, unit="h") + pd.to_timedelta(minute, unit="m") + pd.to_timedelta(second, unit="s")

model_df["DateTime"] = model_df["time"].apply(parse_model_time)

# Select relevant columns and rename
model_df = model_df[["DateTime", "salt"]].rename(columns={"salt": "Reading"})
model_df["Variable"] = "Salinity (PSU)"
model_df["Site"] = "Model"
model_df["Agency"] = "Model"

# Load field data
field_fp = "Data/data-warehouse/parquet/WQ/Salinity.parquet"
field_df = pd.read_parquet(field_fp)
print("Unique field sites:", field_df["Site"].unique())
print("Available field data columns:", field_df.columns)




# Ensure datetime column is named 'DateTime' for consistency
if "DateTime" not in field_df.columns:
    if {"Date", "Time"}.issubset(field_df.columns):
        field_df["Time"] = field_df["Time"].apply(lambda x: "00:00:00" if x == "24:00:00" else x)
        field_df["DateTime"] = pd.to_datetime(field_df["Date"] + " " + field_df["Time"], errors='coerce')
    elif "Date" in field_df.columns:
        field_df["DateTime"] = pd.to_datetime(field_df["Date"], errors='coerce')
    else:
        raise ValueError("Field data must contain either 'DateTime' or 'Date'/'Time' columns")

field_df = field_df.dropna(subset=["DateTime"])

# Select and rename columns for consistency
if "Reading" in field_df.columns:
    field_df = field_df.rename(columns={"Reading": "Value"})
else:
    raise ValueError("Field data must contain 'Reading' column")

field_df["Variable"] = "Salinity (PSU)"

# If 'Site' or 'Agency' columns missing, fill with unknown
if "Site" not in field_df.columns:
    field_df["Site"] = "Field"
if "Agency" not in field_df.columns:
    field_df["Agency"] = "Field"

# Combine model and field data
combined_df = pd.concat([model_df[["DateTime", "Reading", "Variable", "Site", "Agency"]].rename(columns={"Reading": "Value"}),
                         field_df[["DateTime", "Value", "Variable", "Site", "Agency"]]],
                        ignore_index=True)

# Filter to temperature variable only (should be all)
combined_df = combined_df[combined_df["Variable"] == "Salinity (PSU)"]

# Plotting
fig, ax = plt.subplots(figsize=(15, 7))

# Prepare sites and agencies for plotting
sites = combined_df["Site"].unique()

for site in sites:
    site_data = combined_df[combined_df["Site"] == site].copy()
    if site_data.empty:
        continue
    agency = site_data["Agency"].iloc[0]
    style_key = site
    # If site not in plot_styles, fallback to agency or default
    if style_key not in plot_styles:
        style_key = agency
    if style_key not in plot_styles:
        style_key = "Model" if site == "Model" else "USGS"
    style = plot_styles.get(style_key, plot_styles["Model"])

    # Sort data by datetime
    site_data = site_data.sort_values("DateTime")

    if style["marker"]:
        ax.scatter(site_data["DateTime"], site_data["Value"], color=style["color"], marker=style["marker"], label=style["label"])
    else:
        ax.plot(site_data["DateTime"], site_data["Value"], color=style["color"], linestyle=style["linestyle"], label=style["label"])

# Formatting x-axis
ax.set_xlim(xlim_start, xlim_end)

plt.axvspan(pd.Timestamp("2011-01-01"), pd.Timestamp("2012-01-01"), color='gray', alpha=0.08)
plt.axvspan(pd.Timestamp("2013-01-01"), pd.Timestamp("2014-01-01"), color='gray', alpha=0.08)
plt.axvspan(pd.Timestamp("2015-01-01"), pd.Timestamp("2016-01-01"), color='gray', alpha=0.08)
plt.axvspan(pd.Timestamp("2017-01-01"), pd.Timestamp("2018-01-01"), color='gray', alpha=0.08)
plt.axvspan(pd.Timestamp("2019-01-01"), pd.Timestamp("2020-01-01"), color='gray', alpha=0.08)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=xtickint))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)

ax.set_ylabel("Salinity (PSU)")
ax.set_title("Lake Salinity Time Series: Model vs Field Data")
ax.legend()
ax.grid(True)

plt.tight_layout()

# Save figure
plt.savefig("Code/plotting/lake_temperature_comparison.png", dpi=300)
plt.show()
