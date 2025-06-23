"""
Script: compare_multiple_models_threepanel.py

Description:
    This script generates a three-panel time series plot comparing the output from
    multiple water quality and hydrodynamic model runs. It focuses on three key variables:
    - Water Level (m AHD)
    - Temperature (°C)
    - Salinity (PSU)

Design:
    - Accepts a configurable list of model directories, each with its own color and label
    - Reads lake level and water quality output from lake.csv and WQ_1.csv
    - Harmonizes model time formats including 24:00:00 and 25:00:00 cases
    - Creates a 3-row subplot layout for aligned comparison
    - Plots all models as colored line plots with legends identifying each run

Inputs:
    - lake.csv and WQ_1.csv inside each model output directory (specified in config section)

Output:
    - PNG image saved as Code/plotting/comparison_3panel.png

Author: Brendan Busch
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# -------------------- Configuration --------------------

xlim_start = pd.Timestamp("2010-01-01")
xlim_end = pd.Timestamp("2024-01-01")
xtickint = 1

# -------------------- Model Configuration --------------------

model_configs = [
    {"dir": "Model/richmond/output", "color": "red", "label": "Model A"},
    {"dir": "Model/richmond/output_2", "color": "blue", "label": "Model B"},
    {"dir": "Model/richmond/output_3", "color": "green", "label": "Model C"},
]

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
        color = color_map.get(site, "gray")
        ax.plot(site_df["DateTime"], site_df["Reading"], label=site, color=color)

    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.YearLocator(xtickint))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(xlim_start, xlim_end)

# -------------------- Load Data --------------------

df_level = pd.DataFrame()
df_temp = pd.DataFrame()
df_sal = pd.DataFrame()

for config in model_configs:
    level_path = os.path.join(config["dir"], "lake.csv")
    wq_path = os.path.join(config["dir"], "WQ_1.csv")

    # Load lake level
    model_level = pd.read_csv(level_path)
    model_level["time"] = model_level["time"].str.replace("24:00:00", "00:00:00")
    model_level["DateTime"] = pd.to_datetime(model_level["time"], errors='coerce') + pd.to_timedelta(model_level["time"].str.contains("24:00:00").astype(int), unit='D')
    model_level["Reading"] = model_level["Lake Level"] - 14.6
    model_level["Agency"] = config["label"]
    model_level["Site"] = config["label"]
    model_level["Variable"] = "Water Level"
    df_level = pd.concat([df_level, model_level[["Agency", "Site", "DateTime", "Variable", "Reading"]]])

    # Load WQ
    model_wq = load_model_wq(wq_path)

    model_temp = model_wq.copy()
    model_temp["Reading"] = model_temp["temp"]
    model_temp["Agency"] = config["label"]
    model_temp["Site"] = config["label"]
    model_temp["Variable"] = "Temperature"
    df_temp = pd.concat([df_temp, model_temp[["Agency", "Site", "DateTime", "Variable", "Reading"]]])

    model_sal = model_wq.copy()
    model_sal["Reading"] = model_sal["salt"]
    model_sal["Agency"] = config["label"]
    model_sal["Site"] = config["label"]
    model_sal["Variable"] = "Salinity"
    df_sal = pd.concat([df_sal, model_sal[["Agency", "Site", "DateTime", "Variable", "Reading"]]])

# Build color_map before plotting
color_map = {config["label"]: config["color"] for config in model_configs}

# -------------------- Plotting --------------------

fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

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
