"""
Script: compare_model_field_threepanel.py

Description:
    This script generates a three-panel comparison plot for model output and field data
    across three key variables: Water Level, Temperature, and Salinity.

Key Features:
    - Loads model and field data from separate sources
    - Harmonizes datetime formats and variable naming
    - Configurable plot styles per variable and site
    - Produces a single figure with three aligned subplots

Inputs:
    - Model files: lake.csv, WQ_1.csv
    - Field data: lakelevel.parquet, Temperature.parquet, Salinity.parquet

Output:
    - Combined plot with 3 subplots saved to Code/plotting/comparison_3panel.png

Author: Brendan Busch
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# -------------------- Configuration --------------------

xlim_start = pd.Timestamp("2010-01-01")
xlim_end = pd.Timestamp("2023-01-01")
xtickint = 1

plot_styles = {
    "Model":        {"kind": "line", "color": "red"},
    "Board":  {"kind": "scatter", "color": "gold"},
    "Logger (MSc)":   {"kind": "scatter", "color": "orange"},
    "s6142501":     {"kind": "scatter", "color": "blue"},
    "Logger":       {"kind": "scatter", "color": "orange"},
    "Board (2018)":           {"kind": "scatter", "color": "black"},
    "Logger (2018)":       {"kind": "scatter", "color": "green"},
    "Board (MSc)":         {"kind": "scatter", "color": "pink"},
    "Logger (MSc)":   {"kind": "scatter", "color": "brown"},
    "Board (2022)":        {"kind": "scatter", "color": "cyan"},
}

# -------------------- Helper Function --------------------

def load_model_wq(path):
    df = pd.read_csv(path)
    df["time"] = df["time"].str.replace("25:00:00", "01:00:00")
    df["DateTime"] = pd.to_datetime(df["time"], errors='coerce') + pd.to_timedelta(df["time"].str.contains("25:00:00").astype(int), unit='D')
    return df

def apply_plot(ax, df, ylabel, variable_filter):
    for site in df["Site"].unique():
        site_df = df[df["Site"] == site]
        label = f"{site_df['Agency'].iloc[0]} - {site}"
        style = plot_styles.get(site, {"kind": "line", "color": "gray"})
        if style["kind"] == "line":
            ax.plot(site_df["DateTime"], site_df["Reading"], label=label, color=style["color"])
        elif style["kind"] == "scatter":
            ax.scatter(site_df["DateTime"], site_df["Reading"], label=label, color=style["color"], s=5)

    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.YearLocator(xtickint))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(xlim_start, xlim_end)

# -------------------- Load Data --------------------

# Lake Level
field_level = pd.read_parquet("Data/data-warehouse/parquet/level/lakelevel.parquet")
model_level = pd.read_csv("Model/richmond/output/lake.csv")
model_level["time"] = model_level["time"].str.replace("24:00:00", "00:00:00")
model_level["DateTime"] = pd.to_datetime(model_level["time"], errors='coerce') + pd.to_timedelta(model_level["time"].str.contains("24:00:00").astype(int), unit='D')
model_level["Reading"] = model_level["Lake Level"] - 14.6
model_level["Agency"] = "Model"
model_level["Site"] = "Model"
model_level["Variable"] = "Water Level"
model_level = model_level[["Agency", "Site", "DateTime", "Variable", "Reading"]]

df_level = pd.concat([field_level, model_level], ignore_index=True)

# Temperature
field_temp = pd.read_parquet("Data/data-warehouse/parquet/WQ/Temperature.parquet")
model_wq = load_model_wq("Model/richmond/output/WQ_1.csv")
model_temp = model_wq.copy()
model_temp["Reading"] = model_temp["temp"]
model_temp["Agency"] = "Model"
model_temp["Site"] = "Model"
model_temp["Variable"] = "Temperature"
model_temp = model_temp[["Agency", "Site", "DateTime", "Variable", "Reading"]]

df_temp = pd.concat([field_temp, model_temp], ignore_index=True)

# Salinity
field_sal = pd.read_parquet("Data/data-warehouse/parquet/WQ/Salinity.parquet")
model_sal = model_wq.copy()
model_sal["Reading"] = model_sal["salt"]
model_sal["Agency"] = "Model"
model_sal["Site"] = "Model"
model_sal["Variable"] = "Salinity"
model_sal = model_sal[["Agency", "Site", "DateTime", "Variable", "Reading"]]

df_sal = pd.concat([field_sal, model_sal], ignore_index=True)

# -------------------- Plotting --------------------

fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

apply_plot(axes[0], df_level, "Lake Level (mAHD)", "Water Level")
axes[0].set_title("Lake Level Comparison")

apply_plot(axes[1], df_temp, "Temperature (°C)", "Temperature")
axes[1].set_title("Temperature Comparison")

apply_plot(axes[2], df_sal, "Salinity (PSU)", "Salinity")
axes[2].set_title("Salinity Comparison")

axes[2].set_xlabel("Year")
fig.autofmt_xdate()


# Add individual legends to each subplot in the upper left corner
axes[0].legend(loc='upper left',bbox_to_anchor=(1, 1.03))
axes[1].legend(loc='upper left',bbox_to_anchor=(1, 1.03))
axes[2].legend(loc='upper left',bbox_to_anchor=(1, 1.03))

fig.tight_layout()

plt.savefig("Code/plotting/comparison_3panel.png", dpi=300)
plt.show()
