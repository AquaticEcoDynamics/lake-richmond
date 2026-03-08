import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer, CRS
from scipy.interpolate import interp1d
import cmocean

# ── Configuration ──

# Figures to produce: each entry is a list of [left_var, right_var]
figures = [
    ["Temp. [degC]", "Density [kg/m3]"],
    ["EC25 [uS/cm]", "Sal."],
    ["pH", "Chl-a [ug/l]"],
    ["DO [mg/l]", "DO [%]"],
]

variable_config = {
    "Temp. [degC]": {"label": "Temperature (°C)", "vmin": 13, "vmax": 23, "cmap": "cmo.thermal", "contour_interval": 1, "contour_labels": True},
    "Sal.": {"label": "Salinity (PSU)", "vmin": 0.4, "vmax": 0.6, "cmap": "cmo.haline"},
    "Cond. [mS/cm]": {"label": "Conductivity (mS/cm)", "vmin": 0, "vmax": 60, "cmap": "viridis"},
    "EC25 [uS/cm]": {"label": "EC25 (µS/cm)", "vmin": 600, "vmax": 1400, "cmap": "cmo.haline", "contour_interval": 50, "contour_labels": True},
    "Density [kg/m3]": {"label": "Density (kg/m³)", "vmin": 997.5, "vmax": 1000.0, "cmap": "cmo.dense"},
    "Chl-Flu. [ppb]": {"label": "Chlorophyll Fluorescence (ppb)", "vmin": 0, "vmax": 100, "cmap": "viridis"},
    "Chl-a [ug/l]": {"label": "Chlorophyll-a (µg/L)", "vmin": 0, "vmax": 15, "cmap": "cmo.algae", "clip_bottom": 0.5},
    "Turb. [FTU]": {"label": "Turbidity (FTU)", "vmin": 0, "vmax": 200, "cmap": "viridis"},
    "pH": {"label": "pH", "vmin": 6, "vmax": 9, "cmap": "RdYlBu_r", "clip_bottom": 0.5, "contour_interval": 0.5, "contour_labels": True},
    "ORP [mV]": {"label": "ORP (mV)", "vmin": -300, "vmax": 300, "cmap": "viridis"},
    "DO [%]": {"label": "DO (%)", "vmin": 0, "vmax": 120, "cmap": "cmo.oxy"},
    "DO [mg/l]": {"label": "DO (mg/L)", "vmin": 2, "vmax": 10, "cmap": "cmo.oxy", "contour_interval": 1, "contour_labels": True},
    "Quant. [umol/(m2*s)]": {"label": "PAR (µmol/m²/s)", "vmin": 0, "vmax": 1500, "cmap": "viridis"},
}

campaign_folder_map = {
    "2025-03-22": "2025-03-22",
    "2025-05-09": "2025-05-09",
    "2025-08-17": "2025-08-17",
    "2025-10-18": "2025-10-18",
}

surface_level_mAHD = {
    "2025-03-22": 0.5,
    "2025-05-09": 0.48,
    "2025-08-17": 2.1,
    "2025-10-18": 1.8,
}

# Options
show_max_profile_depth = True
show_bottom_depth = False
ref_elev = 0.6
ylim = (-13.2, 2.8)

# Grid resolution
n_depth = 300
n_dist = 300

# ── Setup ──

index_path = "Data/data-lake/UWA/index_march_2025.xlsx"
index_df = pd.read_excel(index_path)
index_df["Campaign"] = index_df["Campaign"].astype(str).str.split(" ").str[0]

crs_from = CRS.from_epsg(4326)
crs_to = CRS.from_epsg(32750)
transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)

data_base = "Data/data-lake/UWA/WQ profiling/FINAL"
output_base = "Code/plotting/profiler/Profiler_v2"

# Reference bathymetry
ref_campaign = "2025-03-22"
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
ref_surface = surface_level_mAHD.get(ref_campaign, 0.0)
ref_df["Bottom_mAHD"] = ref_surface - ref_df["Bottom Depth"]

xi_ref = np.linspace(ref_xmin, ref_xmax, 300)
bottom_interp_ref = np.interp(xi_ref, ref_df["Distance_m"], ref_df["Bottom_mAHD"])

campaigns = list(index_df["Campaign"].unique())


# ── Helper: load and interpolate one variable for one campaign ──

def load_and_interpolate(campaign, var):
    camp_df = index_df[index_df["Campaign"] == campaign].copy().reset_index(drop=True)
    utm_coords = [transformer.transform(lon, lat) for lat, lon in zip(camp_df["Lat"], camp_df["Long"])]
    distances = [0.0]
    for i in range(1, len(utm_coords)):
        x0, y0 = utm_coords[i - 1]
        x1, y1 = utm_coords[i]
        distances.append(distances[-1] + np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2))
    camp_df["Distance_m"] = distances

    wl_mAHD = surface_level_mAHD.get(campaign, 0.0)
    camp_df["Bottom_mAHD"] = wl_mAHD - camp_df["Bottom Depth"]

    folder_name = campaign_folder_map.get(campaign, campaign)
    data_dir = os.path.join(data_base, folder_name)

    profiles = []
    max_profile_depth_mAHD = {}

    for _, row in camp_df.iterrows():
        fname = row["Filename"]
        if pd.isna(fname) or "Buffer" in str(fname):
            continue
        file_path = os.path.join(data_dir, fname)
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='latin-1') as fh:
            for line_idx, line in enumerate(fh):
                if line.strip() == '[Item]':
                    skip = line_idx + 1
                    break
            else:
                skip = 0

        df_prof = pd.read_csv(file_path, skiprows=skip, encoding='latin-1')
        df_prof.columns = [c.strip().replace('\xef\xbf\xbd', 'u').replace('\xb5', 'u').replace('\ufffd', 'u') for c in df_prof.columns]
        df_prof = df_prof.loc[:, ~df_prof.columns.str.startswith("Unnamed")]
        df_prof = df_prof.loc[:, ~df_prof.columns.duplicated()]
        drop_cols = [c for c in df_prof.columns if c in ["Date", "Mark"] or c.startswith("Depth [m].")]
        df_prof.drop(columns=drop_cols, inplace=True, errors="ignore")

        df_prof.rename(columns={"Depth [m]": "Depth"}, inplace=True)
        df_prof["Depth"] = pd.to_numeric(df_prof["Depth"], errors="coerce")
        df_prof.dropna(subset=["Depth"], inplace=True)
        df_prof["Elev_mAHD"] = wl_mAHD - df_prof["Depth"]
        df_prof.sort_values("Elev_mAHD", inplace=True)

        site_id = str(row["Site ID"])
        min_elev = df_prof["Elev_mAHD"].min()
        if pd.notna(min_elev):
            max_profile_depth_mAHD[site_id] = min(max_profile_depth_mAHD.get(site_id, np.inf), min_elev)

        if var in df_prof.columns:
            clip_bot = variable_config.get(var, {}).get("clip_bottom", 0)
            if clip_bot > 0:
                clip_elev = df_prof["Elev_mAHD"].min() + clip_bot
                df_prof = df_prof[df_prof["Elev_mAHD"] >= clip_elev]
            profiles.append((row["Distance_m"], df_prof["Elev_mAHD"].values, df_prof[var].values))

    if not profiles:
        return None, camp_df, max_profile_depth_mAHD, wl_mAHD

    all_elevs = np.concatenate([p[1] for p in profiles])
    elev_min = all_elevs.min()
    elev_max = min(all_elevs.max(), wl_mAHD)
    zi_elevs = np.linspace(elev_min, elev_max, n_depth)

    dist_to_profiles = {}
    for dist_m, depths, values in profiles:
        if dist_m not in dist_to_profiles:
            dist_to_profiles[dist_m] = ([], [])
        dist_to_profiles[dist_m][0].append(depths)
        dist_to_profiles[dist_m][1].append(values)

    unique_dists = sorted(dist_to_profiles.keys())
    profile_matrix = np.full((n_depth, len(unique_dists)), np.nan)

    for j, dist_m in enumerate(unique_dists):
        all_d = np.concatenate(dist_to_profiles[dist_m][0])
        all_v = np.concatenate(dist_to_profiles[dist_m][1])
        valid = np.isfinite(all_d) & np.isfinite(all_v)
        all_d, all_v = all_d[valid], all_v[valid]
        if len(all_d) < 2:
            continue
        sort_idx = np.argsort(all_d)
        all_d, all_v = all_d[sort_idx], all_v[sort_idx]
        f_vert = interp1d(all_d, all_v, kind='linear', bounds_error=False, fill_value=np.nan)
        col = f_vert(zi_elevs)
        # Extend upward to water surface
        prof_max_elev = all_d[-1]
        if prof_max_elev < wl_mAHD:
            col[(zi_elevs > prof_max_elev) & (zi_elevs <= wl_mAHD)] = all_v[-1]
        # Extend downward by half gap
        prof_min_elev = all_d[0]
        if prof_min_elev > elev_min:
            extend_to = prof_min_elev - 0.5 * (prof_min_elev - elev_min)
            col[(zi_elevs < prof_min_elev) & (zi_elevs >= extend_to)] = all_v[0]
        profile_matrix[:, j] = col

    xi = np.linspace(unique_dists[0], unique_dists[-1], n_dist)
    Zi = np.full((n_depth, n_dist), np.nan)
    for i in range(n_depth):
        row_vals = profile_matrix[i, :]
        valid = np.isfinite(row_vals)
        if valid.sum() < 2:
            continue
        f_horiz = interp1d(np.array(unique_dists)[valid], row_vals[valid], kind='linear', bounds_error=False, fill_value=np.nan)
        Zi[i, :] = f_horiz(xi)

    Xi, Yi = np.meshgrid(xi, zi_elevs)
    return (Xi, Yi, Zi), camp_df, max_profile_depth_mAHD, wl_mAHD


# ── Build multi-panel figures ──

n_rows = len(campaigns)
os.makedirs(output_base, exist_ok=True)

for panel_vars in figures:
    n_cols = len(panel_vars)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(8.27, 10.69),
                              sharex=True, sharey=True)

    for row_idx, campaign in enumerate(campaigns):
        for col_idx, var in enumerate(panel_vars):
            ax = axes[row_idx, col_idx]
            config = variable_config.get(var, {"label": var, "vmin": None, "vmax": None})
            cmap = config.get("cmap", "viridis")

            result, camp_df, max_prof_depth, wl_mAHD = load_and_interpolate(campaign, var)

            if result is not None:
                Xi, Yi, Zi = result
                if config["vmin"] is not None and config["vmax"] is not None:
                    levels = np.linspace(config["vmin"], config["vmax"], 100)
                    zi_clipped = np.clip(Zi, config["vmin"], config["vmax"])
                    contour = ax.contourf(Xi, Yi, zi_clipped, levels=levels, cmap=cmap,
                                           vmin=config["vmin"], vmax=config["vmax"])
                else:
                    contour = ax.contourf(Xi, Yi, Zi, cmap=cmap)

                # Contour lines if configured
                ci = config.get("contour_interval")
                if ci and config["vmin"] is not None and config["vmax"] is not None:
                    cline_levels = np.arange(config["vmin"], config["vmax"] + ci, ci)
                    cs = ax.contour(Xi, Yi, Zi, levels=cline_levels, colors='k', linewidths=0.3, zorder=5)
                    if config.get("contour_labels"):
                        ax.clabel(cs, inline=True, fontsize=4, fmt='%g')

                cbar = fig.colorbar(contour, ax=ax, pad=0.02, aspect=20)
                if config["vmin"] is not None and config["vmax"] is not None:
                    cbar.set_ticks(np.linspace(config["vmin"], config["vmax"], num=5))
                cbar.set_label(config["label"], fontsize=7)
                cbar.ax.tick_params(labelsize=6)

            # Site markers and labels
            n_sites = len(camp_df)
            buffer = min(2, n_sites // 4)
            plot_sites = camp_df.iloc[buffer:n_sites - buffer] if buffer > 0 and n_sites > 2 * buffer else camp_df
            ax.scatter(plot_sites["Distance_m"], [ylim[1]] * len(plot_sites),
                       color='k', marker='o', s=6, zorder=11, clip_on=False)
            for _, site_row in plot_sites.iterrows():
                ax.text(site_row["Distance_m"], ylim[1] - 0.6, str(site_row["Site ID"]),
                        ha='center', va='bottom', fontsize=4, color='k', zorder=11)

            # Max profile depth markers
            if show_max_profile_depth and max_prof_depth:
                mx, my = [], []
                for _, site_row in plot_sites.iterrows():
                    sid = str(site_row["Site ID"])
                    if sid in max_prof_depth:
                        mx.append(site_row["Distance_m"])
                        my.append(max_prof_depth[sid])
                if mx:
                    ax.scatter(mx, my, color='k', marker='+', s=4, linewidths=0.3, zorder=11)

            # Bathymetry mask
            ax.fill_between(xi_ref, bottom_interp_ref, ylim[0], color="gray", alpha=1.0, zorder=10)

            # Reference elevation line
            ax.axhline(y=ref_elev, color='gray', linestyle='--', linewidth=0.4, zorder=9)
            if col_idx == n_cols - 1:
                ax.text(ref_xmin + 5, ref_elev + 0.3, f"{ref_elev} mAHD", fontsize=4, color='gray', ha='left', va='bottom', zorder=12)

            ax.set_xlim(ref_xmin, ref_xmax)
            ax.set_ylim(ylim)

            # Campaign date label in bottom-left corner
            ax.text(0.02, 0.04, campaign, transform=ax.transAxes,
                    fontsize=8, fontweight='bold', va='bottom', ha='left', zorder=12)

            # Titles: variable on top row, campaign on left column
            if row_idx == 0:
                ax.set_title(config["label"], fontsize=7, fontweight='bold')
                ax.text(0.0, 1.01, "N", transform=ax.transAxes, fontsize=7, fontweight='bold', ha='left', va='bottom')
                ax.text(1.0, 1.01, "S", transform=ax.transAxes, fontsize=7, fontweight='bold', ha='right', va='bottom')
            if col_idx == 0:
                ax.set_ylabel("Elevation (mAHD)", fontsize=5)
            else:
                ax.set_ylabel("")
            if row_idx == n_rows - 1:
                ax.set_xlabel("Distance (m)", fontsize=5)
            ax.tick_params(labelsize=6)

            # Custom annotations
            if var == "Chl-a [ug/l]" and row_idx == n_rows - 1:
                ax.text(200, -2, "DCM", fontsize=6, fontweight='bold', ha='center', va='center', zorder=12)

    fig.tight_layout(h_pad=0.5, w_pad=0.8)

    safe_names = "_".join([v.replace(" ", "").replace("[", "").replace("]", "").replace(".", "").replace("/", "") for v in panel_vars])
    filepath = os.path.join(output_base, f"multipanel_{safe_names}.png")
    fig.savefig(filepath, dpi=300)
    plt.close(fig)
    print(f"Saved: {filepath}")
