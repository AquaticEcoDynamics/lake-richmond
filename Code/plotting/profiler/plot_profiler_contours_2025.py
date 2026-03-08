import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer, CRS
from scipy.interpolate import griddata
import cmocean

# Configuration for profiler variable display names and colorbar limits
variable_config = {
    "Temp. [degC]": {"label": "Temperature (°C)", "vmin": 18, "vmax": 26, "cmap": "viridis"},
    "Sal.": {"label": "Salinity (PSU)", "vmin": 0.4, "vmax": 0.6, "cmap": "viridis"},
    "Cond. [mS/cm]": {"label": "Conductivity (mS/cm)", "vmin": 0, "vmax": 60, "cmap": "viridis"},
    "EC25 [uS/cm]": {"label": "EC25 (µS/cm)", "vmin": 0, "vmax": 60000, "cmap": "viridis"},
    "Density [kg/m3]": {"label": "Density (kg/m³)", "vmin": 1000, "vmax": 1030, "cmap": "viridis"},
    "SigmaT": {"label": "Sigma-T", "vmin": 0, "vmax": 30, "cmap": "viridis"},
    "Chl-Flu. [ppb]": {"label": "Chlorophyll Fluorescence (ppb)", "vmin": 0, "vmax": 100, "cmap": "viridis"},
    "Chl-a [ug/l]": {"label": "Chlorophyll-a (µg/L)", "vmin": 0, "vmax": 100, "cmap": "viridis"},
    "Turb. [FTU]": {"label": "Turbidity (FTU)", "vmin": 0, "vmax": 200, "cmap": "viridis"},
    "pH": {"label": "pH", "vmin": 6, "vmax": 9, "cmap": "viridis"},
    "ORP [mV]": {"label": "ORP (mV)", "vmin": -500, "vmax": 500, "cmap": "viridis"},
    "DO [%]": {"label": "DO (%)", "vmin": 0, "vmax": 150, "cmap": "cmo.oxy"},
    "DO [mg/l]": {"label": "DO (mg/L)", "vmin": 2, "vmax": 10, "cmap": "cmo.oxy"},
    "Quant. [umol/(m2*s)]": {"label": "PAR (µmol/m²/s)", "vmin": 0, "vmax": 2500, "cmap": "viridis"},
}

# Campaign date -> data subfolder mapping
campaign_folder_map = {
    "2025-03-01": "2025-03-22",
    "2025-05-09": "2025-05-09",
    "2025-08-17": "2025-08-17",
    "2025-10-18": "2025-10-18",
}

# Load index file
index_path = "Data/data-lake/UWA/index_march_2025.xlsx"
index_df = pd.read_excel(index_path)
index_df["Campaign"] = index_df["Campaign"].astype(str).str.split(" ").str[0]

# UTM transformer
crs_from = CRS.from_epsg(4326)
crs_to = CRS.from_epsg(32750)
transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)

data_base = "Data/data-lake/UWA/WQ profiling/FINAL"
output_base = "Code/plotting/profiler/Profiler"

# Options
show_max_profile_depth = True

# Build reference bathymetry from the March campaign (most sites / best coverage)
ref_campaign = "2025-03-01"
ref_df = index_df[index_df["Campaign"] == ref_campaign].copy().reset_index(drop=True)
ref_utm = [transformer.transform(lon, lat) for lat, lon in zip(ref_df["Lat"], ref_df["Long"])]
ref_distances = [0.0]
for i in range(1, len(ref_utm)):
    x0, y0 = ref_utm[i - 1]
    x1, y1 = ref_utm[i]
    ref_distances.append(ref_distances[-1] + np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2))
ref_df["Distance_m"] = ref_distances
ref_xmin = ref_df["Distance_m"].min()
ref_xmax = ref_df["Distance_m"].max()

# Process each campaign
campaigns = index_df["Campaign"].unique()

for campaign in campaigns:
    print(f"\n{'='*60}")
    print(f"Processing campaign: {campaign}")
    print(f"{'='*60}")

    camp_df = index_df[index_df["Campaign"] == campaign].copy().reset_index(drop=True)

    # Calculate cumulative distance along the transect using UTM coords
    utm_coords = [transformer.transform(lon, lat) for lat, lon in zip(camp_df["Lat"], camp_df["Long"])]
    distances = [0.0]
    for i in range(1, len(utm_coords)):
        x0, y0 = utm_coords[i - 1]
        x1, y1 = utm_coords[i]
        dist = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        distances.append(distances[-1] + dist)
    camp_df["Distance_m"] = distances

    # Resolve data folder for this campaign
    folder_name = campaign_folder_map.get(campaign, campaign)
    data_dir = os.path.join(data_base, folder_name)

    if not os.path.isdir(data_dir):
        print(f"WARNING: Data folder not found: {data_dir}, skipping campaign.")
        continue

    # Load profiler data
    profiler_data = {}
    max_profile_depth = {}  # Site ID -> max depth reached in profile

    for _, row in camp_df.iterrows():
        fname = row["Filename"]
        if pd.isna(fname) or "Buffer" in str(fname):
            continue

        file_path = os.path.join(data_dir, fname)
        if not os.path.exists(file_path):
            print(f"  WARNING: File not found: {file_path}")
            continue

        # Detect header: find [Item] line to determine skiprows, or read from line 0
        with open(file_path, 'r', encoding='latin-1') as fh:
            for line_idx, line in enumerate(fh):
                if line.strip() == '[Item]':
                    skip = line_idx + 1
                    break
            else:
                skip = 0  # No instrument header — already cleaned file

        df_prof = pd.read_csv(file_path, skiprows=skip, encoding='latin-1')
        print(f"  Loaded {len(df_prof)} rows from {fname} (skiprows={skip})")

        df_prof.columns = [col.strip() for col in df_prof.columns]
        # Normalise encoding artefacts (latin-1 read of UTF-8 µ → ï¿½)
        df_prof.columns = [col.replace('\xef\xbf\xbd', 'u').replace('\xb5', 'u').replace('\ufffd', 'u') for col in df_prof.columns]
        # Drop duplicate / junk columns
        df_prof = df_prof.loc[:, ~df_prof.columns.str.startswith("Unnamed")]
        df_prof = df_prof.loc[:, ~df_prof.columns.duplicated()]
        # Drop non-measurement columns and duplicates like "Depth [m].1"
        drop_cols = [c for c in df_prof.columns if c in ["Date", "Mark"] or c.startswith("Depth [m].")]
        df_prof.drop(columns=drop_cols, inplace=True, errors="ignore")

        df_prof.rename(columns={"Depth [m]": "Depth"}, inplace=True)
        df_prof["Depth"] = pd.to_numeric(df_prof["Depth"], errors="coerce")
        df_prof["Distance_m"] = row["Distance_m"]

        # Track max depth reached per site
        site_id = str(row["Site ID"])
        max_d = df_prof["Depth"].max()
        if pd.notna(max_d):
            max_profile_depth[site_id] = max(max_profile_depth.get(site_id, 0), max_d)

        for col in df_prof.columns:
            if col not in ["Depth", "Distance_m"] and pd.api.types.is_numeric_dtype(df_prof[col]):
                if col not in profiler_data:
                    profiler_data[col] = []
                df_col = df_prof[["Depth", col]].copy()
                df_col["Distance_m"] = row["Distance_m"]
                df_col = df_col.rename(columns={col: "Value"})
                profiler_data[col].append(df_col)

    if not profiler_data:
        print(f"  No data loaded for campaign {campaign}, skipping.")
        continue

    for var in profiler_data:
        profiler_data[var] = pd.concat(profiler_data[var], ignore_index=True)

    print(f"  Variables: {list(profiler_data.keys())}")

    # Create output subfolder for this campaign
    output_dir = os.path.join(output_base, folder_name)
    os.makedirs(output_dir, exist_ok=True)

    # Plot each variable
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

        fig, ax = plt.subplots(figsize=(12 / 2.54, 7 / 2.54))

        config = variable_config.get(var, {"label": var, "vmin": None, "vmax": None})
        cmap = config.get("cmap", "viridis")

        if config["vmin"] is not None and config["vmax"] is not None:
            levels = np.linspace(config["vmin"], config["vmax"], 100)
            zi_clipped = np.clip(zi, config["vmin"], config["vmax"])
            contour = ax.contourf(Xi, Yi, zi_clipped, levels=levels, cmap=cmap, vmin=config["vmin"], vmax=config["vmax"])
        else:
            contour = ax.contourf(Xi, Yi, zi, cmap=cmap)

        ax.invert_yaxis()

        # Mark site positions at surface with labels
        n_sites = len(camp_df)
        buffer = min(2, n_sites // 4)
        plot_sites = camp_df.iloc[buffer:n_sites - buffer] if buffer > 0 and n_sites > 2 * buffer else camp_df
        ax.scatter(plot_sites["Distance_m"], [-1.0] * len(plot_sites), color='k', marker='o', s=10, zorder=11)
        for _, site_row in plot_sites.iterrows():
            ax.text(site_row["Distance_m"], -0.4, str(site_row["Site ID"]),
                    ha='center', va='top', fontsize=3.5, color='k', zorder=11)

        # Mark bottom depth at each profile site
        if "Bottom Depth" in camp_df.columns:
            ax.scatter(plot_sites["Distance_m"], plot_sites["Bottom Depth"],
                       color='k', marker='x', s=8, linewidths=0.5, zorder=11)

        # Mark max profile depth reached at each site
        if show_max_profile_depth and max_profile_depth:
            max_depths_x = []
            max_depths_y = []
            for _, site_row in plot_sites.iterrows():
                sid = str(site_row["Site ID"])
                if sid in max_profile_depth:
                    max_depths_x.append(site_row["Distance_m"])
                    max_depths_y.append(max_profile_depth[sid])
            if max_depths_x:
                ax.scatter(max_depths_x, max_depths_y,
                           color='k', marker='+', s=8, linewidths=0.5, zorder=11)

        ax.set_xlim(ref_xmin, ref_xmax)
        ax.set_ylim(15, -1)

        cbar = fig.colorbar(contour, ax=ax)
        if config["vmin"] is not None and config["vmax"] is not None:
            cbar.set_ticks(np.linspace(config["vmin"], config["vmax"], num=6))
        cbar.set_label(config["label"], fontsize=6)
        cbar.ax.tick_params(labelsize=6)

        if "Bottom Depth" in ref_df.columns:
            xi_ref = np.linspace(ref_xmin, ref_xmax, 300)
            bottom_interp = np.interp(xi_ref, ref_df["Distance_m"], ref_df["Bottom Depth"])
            ax.fill_between(xi_ref, bottom_interp, 15, color="gray", alpha=0.7, zorder=10)

        ax.set_title(f"{config['label']} — {campaign}", fontsize=8)
        ax.set_xlabel("Distance (m)", fontsize=6)
        ax.set_ylabel("Depth (m)", fontsize=6)
        ax.tick_params(labelsize=6)
        fig.tight_layout()

        safe_var = var.replace(" ", "_").replace("[", "").replace("]", "").replace(".", "").replace("/", "")
        filename = f"{safe_var}_{campaign}.png"
        filepath = os.path.join(output_dir, filename)
        fig.savefig(filepath, dpi=300)
        plt.close(fig)
        print(f"  Saved: {filepath}")

print("\nDone.")
