import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pyproj import Transformer, CRS
import numpy as np
import glob
from scipy.interpolate import griddata
import cmocean

# Configuration for profiler variable display names and colorbar limits
variable_config = {
    "Temp. [degC]": {"label": "Temperature (°C)", "vmin": 18, "vmax": 26},
    "Sal.": {"label": "Salinity (PSU)", "vmin": 0.4, "vmax": 0.6},
    "Cond. [mS/cm]": {"label": "Conductivity (mS/cm)", "vmin": 0, "vmax": 60},
    "EC25 [�S/cm]": {"label": "EC25 (µS/cm)", "vmin": 0, "vmax": 60000},
    "Density [kg/m3]": {"label": "Density (kg/m³)", "vmin": 1000, "vmax": 1030},
    "SigmaT": {"label": "Sigma-T", "vmin": 0, "vmax": 30},
    "Chl-Flu. [ppb]": {"label": "Chlorophyll Fluorescence (ppb)", "vmin": 0, "vmax": 100},
    "Chl-a [�g/l]": {"label": "Chlorophyll-a (µg/L)", "vmin": 0, "vmax": 100},
    "Turb. [FTU]": {"label": "Turbidity (FTU)", "vmin": 0, "vmax": 200},
    "pH": {"label": "pH", "vmin": 6, "vmax": 9},
    "ORP [mV]": {"label": "ORP (mV)", "vmin": -500, "vmax": 500},
    "DO [%]": {"label": "DO (%)", "vmin": 0, "vmax": 150},
    "DO [mg/l]": {"label": "DO (mg/L)", "vmin": 2, "vmax": 10},
    "Quant. [�mol/(m2*s)]": {"label": "PAR (µmol/m²/s)", "vmin": 0, "vmax": 2500},
}

# Load index file
index_path = "Data/data-lake/UWA/index_march_2025.xlsx"
index_df = pd.read_excel(index_path)

# Convert lat/lon to UTM coordinates
crs_from = CRS.from_epsg(4326)
crs_to = CRS.from_epsg(32750)
transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
utm_coords = [transformer.transform(lon, lat) for lat, lon in zip(index_df["Lat"], index_df["Long"])]

# Calculate cumulative distance along the transect using UTM coords
distances = [0.0]
for i in range(1, len(utm_coords)):
    x0, y0 = utm_coords[i - 1]
    x1, y1 = utm_coords[i]
    dist = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    distances.append(distances[-1] + dist)
index_df["Distance_m"] = distances

# Prepare structure for storing profiler data by variable
profiler_data = {}

# Loop through each profiler file
for i, row in index_df.iterrows():
    if "Buffer" in row["Filename"]:
        continue
    file_path = os.path.join("Data/data-lake/UWA/WQ Profiling/AAQ-20250322/RICHMOND", row["Filename"])

    if os.path.exists(file_path):
        df_prof = pd.read_csv(file_path, skiprows=66)
        
        
        print(f"Loaded {len(df_prof)} rows from {row['Filename']}")
        
        
        df_prof.columns = [col.strip() for col in df_prof.columns]
        df_prof.rename(columns={"Depth [m]": "Depth"}, inplace=True)
        df_prof["Depth"] = pd.to_numeric(df_prof["Depth"], errors="coerce")
        df_prof["Distance_m"] = row["Distance_m"]

        for col in df_prof.columns:
            if col not in ["Depth", "Distance_m"] and pd.api.types.is_numeric_dtype(df_prof[col]):
                if col not in profiler_data:
                    profiler_data[col] = []
                df_col = df_prof[["Depth", col]].copy()
                df_col["Distance_m"] = row["Distance_m"]
                df_col = df_col.rename(columns={col: "Value"})
                profiler_data[col].append(df_col)

# Concatenate and structure by variable
for var in profiler_data:
    profiler_data[var] = pd.concat(profiler_data[var], ignore_index=True)

print("Available variables for plotting:", list(profiler_data.keys()))

# Generate and save plots for each variable
output_dir = "Code/plotting/Profiler"
os.makedirs(output_dir, exist_ok=True)

for var, df_plot in profiler_data.items():
    xi = np.linspace(df_plot["Distance_m"].min(), df_plot["Distance_m"].max(), 300)
    yi = np.linspace(df_plot["Depth"].min(), df_plot["Depth"].max(), 300)
    Xi, Yi = np.meshgrid(xi, yi)

    zi = griddata(
        (df_plot["Distance_m"], df_plot["Depth"]),
        df_plot["Value"],
        (Xi, Yi),
        method="linear"
    )

    fig, ax = plt.subplots(figsize=(12/2.54, 7/2.54))  # Convert cm to inches

    config = variable_config.get(var, {"label": var, "vmin": None, "vmax": None})
    print(f"Plotting variable: {var}, vmin: {config['vmin']}, vmax: {config['vmax']}")
    cmap = "cmo.oxy" if var == "DO [mg/l]" else "viridis"
    if config["vmin"] is not None and config["vmax"] is not None:
        levels = np.linspace(config["vmin"], config["vmax"], 100)
        zi_clipped = np.clip(zi, config["vmin"], config["vmax"])
        contour = ax.contourf(Xi, Yi, zi_clipped, levels=levels, cmap=cmap, vmin=config["vmin"], vmax=config["vmax"])
    else:
        contour = ax.contourf(Xi, Yi, zi, cmap=cmap)
    print(f"Contour levels range: {contour.get_clim()}")
    ax.invert_yaxis()
    ax.scatter(index_df["Distance_m"][2:-2], [-0.5] * (len(index_df) - 4), color='k', marker='o', s=10, zorder=11)

    ax.set_ylim(15, -0.5)
    
    
    cbar = fig.colorbar(contour, ax=ax)
    if config["vmin"] is not None and config["vmax"] is not None:
        cbar.set_ticks(np.linspace(config["vmin"], config["vmax"], num=6))
    cbar.set_label(config["label"], fontsize=6)
    cbar.ax.tick_params(labelsize=6)

    if "Bottom Depth" in index_df.columns:
        bottom_interp = np.interp(xi, index_df["Distance_m"], index_df["Bottom Depth"])
        ax.fill_between(xi, bottom_interp, 15, color="gray", zorder=10)

    ax.set_title(config["label"], fontsize=8)
    ax.set_xlabel("Distance (m)", fontsize=6)
    ax.set_ylabel("Depth (m)", fontsize=6)
    ax.tick_params(labelsize=6)
    fig.tight_layout()

    campaign = index_df["Campaign"].iloc[0] if "Campaign" in index_df.columns else "unknown"
    safe_var = var.replace(" ", "_").replace("[", "").replace("]", "").replace(".", "").replace("/", "")
    filename = f"{safe_var}_{campaign}.png"
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=300)
    plt.close(fig)
