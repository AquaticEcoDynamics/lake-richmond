import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer, CRS
from scipy.interpolate import interp1d
import cmocean

# Configuration for profiler variable display names and colorbar limits
variable_config = {
    "Temp. [degC]": {"label": "Temperature (°C)", "vmin": 13, "vmax": 23, "cmap": "cmo.thermal"},
    "Sal.": {"label": "Salinity (PSU)", "vmin": 0.4, "vmax": 0.6, "cmap": "cmo.haline"},
    "Cond. [mS/cm]": {"label": "Conductivity (mS/cm)", "vmin": 0, "vmax": 60, "cmap": "viridis"},
    "EC25 [uS/cm]": {"label": "EC25 (µS/cm)", "vmin": 600, "vmax": 1400, "cmap": "cmo.haline"},
    "Density [kg/m3]": {"label": "Density (kg/m³)", "vmin": 997.5, "vmax": 1000.0, "cmap": "cmo.dense"},
    "Chl-Flu. [ppb]": {"label": "Chlorophyll Fluorescence (ppb)", "vmin": 0, "vmax": 100, "cmap": "viridis"},
    "Chl-a [ug/l]": {"label": "Chlorophyll-a (µg/L)", "vmin": 0, "vmax": 15, "cmap": "cmo.algae"},
    "Turb. [FTU]": {"label": "Turbidity (FTU)", "vmin": 0, "vmax": 200, "cmap": "viridis"},
    "pH": {"label": "pH", "vmin": 6, "vmax": 9, "cmap": "RdYlBu_r"},
    "ORP [mV]": {"label": "ORP (mV)", "vmin": -300, "vmax": 300, "cmap": "viridis"},
    "DO [%]": {"label": "DO (%)", "vmin": 0, "vmax": 120, "cmap": "cmo.oxy"},
    "DO [mg/l]": {"label": "DO (mg/L)", "vmin": 2, "vmax": 10, "cmap": "cmo.oxy"},
    "Quant. [umol/(m2*s)]": {"label": "PAR (µmol/m²/s)", "vmin": 0, "vmax": 1500, "cmap": "viridis"},
}

# Campaign date -> data subfolder mapping
campaign_folder_map = {
    "2025-03-22": "2025-03-22",
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
output_base = "Code/plotting/profiler/Profiler_v2"

# Options
show_max_profile_depth = True
show_bottom_depth = False

# Grid resolution
n_depth = 300   # vertical grid points
n_dist = 300    # horizontal grid points

# Water surface level (mAHD) for each campaign
# depth_below_surface = surface_level - elevation_mAHD
# elevation_mAHD = surface_level - depth_below_surface
surface_level_mAHD = {
    "2025-03-22": 0.5,
    "2025-05-09": 0.48,
    "2025-08-17": 2.1,
    "2025-10-18": 1.8,
}

# Build reference bathymetry from the March campaign (most sites / best coverage)
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
# Convert reference bottom depth to mAHD
ref_surface = surface_level_mAHD.get(ref_campaign, 0.0)
ref_df["Bottom_mAHD"] = ref_surface - ref_df["Bottom Depth"]

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

    # Surface level for this campaign
    wl_mAHD = surface_level_mAHD.get(campaign, 0.0)

    # Convert bottom depths to mAHD for this campaign
    camp_df["Bottom_mAHD"] = wl_mAHD - camp_df["Bottom Depth"]

    # ── Load profiler data, keeping per-site structure ──
    # site_profiles[var] = list of (distance, elevation_array, value_array) per site
    site_profiles = {}
    max_profile_depth_mAHD = {}  # Site ID -> lowest elevation (mAHD) reached
    loaded_sites = []       # track (index, distance, site_id) for sites with data

    for idx, row in camp_df.iterrows():
        fname = row["Filename"]
        if pd.isna(fname) or "Buffer" in str(fname):
            continue

        file_path = os.path.join(data_dir, fname)
        if not os.path.exists(file_path):
            print(f"  WARNING: File not found: {file_path}")
            continue

        # Detect header
        with open(file_path, 'r', encoding='latin-1') as fh:
            for line_idx, line in enumerate(fh):
                if line.strip() == '[Item]':
                    skip = line_idx + 1
                    break
            else:
                skip = 0

        df_prof = pd.read_csv(file_path, skiprows=skip, encoding='latin-1')
        print(f"  Loaded {len(df_prof)} rows from {fname} (skiprows={skip})")

        df_prof.columns = [col.strip() for col in df_prof.columns]
        df_prof.columns = [col.replace('\xef\xbf\xbd', 'u').replace('\xb5', 'u').replace('\ufffd', 'u') for col in df_prof.columns]
        df_prof = df_prof.loc[:, ~df_prof.columns.str.startswith("Unnamed")]
        df_prof = df_prof.loc[:, ~df_prof.columns.duplicated()]
        drop_cols = [c for c in df_prof.columns if c in ["Date", "Mark"] or c.startswith("Depth [m].")]
        df_prof.drop(columns=drop_cols, inplace=True, errors="ignore")

        df_prof.rename(columns={"Depth [m]": "Depth"}, inplace=True)
        df_prof["Depth"] = pd.to_numeric(df_prof["Depth"], errors="coerce")
        df_prof.dropna(subset=["Depth"], inplace=True)
        # Convert depth below surface to elevation mAHD
        df_prof["Elev_mAHD"] = wl_mAHD - df_prof["Depth"]
        df_prof.sort_values("Elev_mAHD", inplace=True)

        site_id = str(row["Site ID"])
        dist_m = row["Distance_m"]
        min_elev = df_prof["Elev_mAHD"].min()
        if pd.notna(min_elev):
            max_profile_depth_mAHD[site_id] = min(max_profile_depth_mAHD.get(site_id, np.inf), min_elev)

        skip_vars = ["Depth", "Elev_mAHD", "SigmaT"]
        for col in df_prof.columns:
            if col not in skip_vars and pd.api.types.is_numeric_dtype(df_prof[col]):
                if col not in site_profiles:
                    site_profiles[col] = []
                site_profiles[col].append((
                    dist_m,
                    df_prof["Elev_mAHD"].values,
                    df_prof[col].values,
                ))

    if not site_profiles:
        print(f"  No data loaded for campaign {campaign}, skipping.")
        continue

    print(f"  Variables: {list(site_profiles.keys())}")

    # Create output subfolder
    output_dir = os.path.join(output_base, folder_name)
    os.makedirs(output_dir, exist_ok=True)

    # ── Two-step interpolation and plotting ──
    for var, profiles in site_profiles.items():
        # Step 1: Build a common elevation grid from all profiles for this variable
        all_elevs = np.concatenate([p[1] for p in profiles])
        elev_min = all_elevs.min()
        elev_max = min(all_elevs.max(), wl_mAHD)
        zi_elevs = np.linspace(elev_min, elev_max, n_depth)

        # Get unique distances (sorted) and interpolate each profile onto common depth grid
        # Group profiles by distance (multiple files may map to same distance)
        dist_to_profiles = {}
        for dist_m, depths, values in profiles:
            if dist_m not in dist_to_profiles:
                dist_to_profiles[dist_m] = ([], [])
            dist_to_profiles[dist_m][0].append(depths)
            dist_to_profiles[dist_m][1].append(values)

        unique_dists = sorted(dist_to_profiles.keys())
        # Matrix: columns = sites, rows = depth levels
        profile_matrix = np.full((n_depth, len(unique_dists)), np.nan)

        for j, dist_m in enumerate(unique_dists):
            all_d = np.concatenate(dist_to_profiles[dist_m][0])
            all_v = np.concatenate(dist_to_profiles[dist_m][1])
            # Sort by depth and remove NaN values
            valid = np.isfinite(all_d) & np.isfinite(all_v)
            all_d = all_d[valid]
            all_v = all_v[valid]
            if len(all_d) < 2:
                continue
            sort_idx = np.argsort(all_d)
            all_d = all_d[sort_idx]
            all_v = all_v[sort_idx]
            # Interpolate vertically onto common elevation grid (no extrapolation)
            f_vert = interp1d(all_d, all_v, kind='linear', bounds_error=False, fill_value=np.nan)
            col = f_vert(zi_elevs)
            # Extend upward to water surface: hold shallowest value
            prof_max_elev = all_d[-1]  # sorted ascending, so last is highest elevation
            if prof_max_elev < wl_mAHD:
                shallowest_val = all_v[-1]
                fill_mask = (zi_elevs > prof_max_elev) & (zi_elevs <= wl_mAHD)
                col[fill_mask] = shallowest_val
            # Extend downward (lower mAHD) by half the gap: hold deepest value
            prof_min_elev = all_d[0]  # sorted ascending, so first is lowest elevation
            if prof_min_elev > elev_min:
                extend_to = prof_min_elev - 0.5 * (prof_min_elev - elev_min)
                deepest_val = all_v[0]
                fill_mask = (zi_elevs < prof_min_elev) & (zi_elevs >= extend_to)
                col[fill_mask] = deepest_val
            profile_matrix[:, j] = col

        # Step 2: Interpolate horizontally at each depth level
        xi = np.linspace(unique_dists[0], unique_dists[-1], n_dist)
        Zi = np.full((n_depth, n_dist), np.nan)

        for i in range(n_depth):
            row_vals = profile_matrix[i, :]
            valid = np.isfinite(row_vals)
            if valid.sum() < 2:
                continue
            dists_valid = np.array(unique_dists)[valid]
            vals_valid = row_vals[valid]
            f_horiz = interp1d(dists_valid, vals_valid, kind='linear', bounds_error=False, fill_value=np.nan)
            Zi[i, :] = f_horiz(xi)

        Xi, Yi = np.meshgrid(xi, zi_elevs)

        # ── Plot ──
        fig, ax = plt.subplots(figsize=(12 / 2.54, 7 / 2.54))

        config = variable_config.get(var, {"label": var, "vmin": None, "vmax": None})
        cmap = config.get("cmap", "viridis")

        if config["vmin"] is not None and config["vmax"] is not None:
            levels = np.linspace(config["vmin"], config["vmax"], 100)
            zi_clipped = np.clip(Zi, config["vmin"], config["vmax"])
            contour = ax.contourf(Xi, Yi, zi_clipped, levels=levels, cmap=cmap, vmin=config["vmin"], vmax=config["vmax"])
        else:
            contour = ax.contourf(Xi, Yi, Zi, cmap=cmap)

        # Mark site positions at surface with labels
        n_sites = len(camp_df)
        buffer = min(2, n_sites // 4)
        plot_sites = camp_df.iloc[buffer:n_sites - buffer] if buffer > 0 and n_sites > 2 * buffer else camp_df
        ax.scatter(plot_sites["Distance_m"], [2.8] * len(plot_sites), color='k', marker='o', s=10, zorder=11, clip_on=False)
        for _, site_row in plot_sites.iterrows():
            ax.text(site_row["Distance_m"], 2.2, str(site_row["Site ID"]),
                    ha='center', va='bottom', fontsize=3.5, color='k', zorder=11)

        # Mark bottom depth at each profile site (converted to mAHD)
        if show_bottom_depth and "Bottom_mAHD" in camp_df.columns:
            ax.scatter(plot_sites["Distance_m"], plot_sites["Bottom_mAHD"],
                       color='k', marker='x', s=8, linewidths=0.5, zorder=11)

        # Mark max profile depth reached at each site (already in mAHD)
        if show_max_profile_depth and max_profile_depth_mAHD:
            max_depths_x = []
            max_depths_y = []
            for _, site_row in plot_sites.iterrows():
                sid = str(site_row["Site ID"])
                if sid in max_profile_depth_mAHD:
                    max_depths_x.append(site_row["Distance_m"])
                    max_depths_y.append(max_profile_depth_mAHD[sid])
            if max_depths_x:
                ax.scatter(max_depths_x, max_depths_y,
                           color='k', marker='+', s=8, linewidths=0.5, zorder=11)

        ax.set_xlim(ref_xmin, ref_xmax)
        ax.set_ylim(-13.2, 2.8)

        cbar = fig.colorbar(contour, ax=ax)
        if config["vmin"] is not None and config["vmax"] is not None:
            cbar.set_ticks(np.linspace(config["vmin"], config["vmax"], num=6))
        cbar.set_label(config["label"], fontsize=6)
        cbar.ax.tick_params(labelsize=6)

        if "Bottom_mAHD" in ref_df.columns:
            xi_ref = np.linspace(ref_xmin, ref_xmax, 300)
            bottom_interp = np.interp(xi_ref, ref_df["Distance_m"], ref_df["Bottom_mAHD"])
            ax.fill_between(xi_ref, bottom_interp, -13.2, color="gray", alpha=0.9, zorder=10)

        # Reference elevation line
        ref_elev = 0.6
        ax.axhline(y=ref_elev, color='gray', linestyle='--', linewidth=0.5, zorder=9)
        ax.text(ref_xmin, ref_elev, f'{ref_elev} mAHD ', va='bottom', ha='right',
                fontsize=3.5, color='gray', clip_on=False)

        ax.set_title(f"{config['label']} — {campaign}", fontsize=8)
        ax.set_xlabel("Distance (m)", fontsize=6)
        ax.set_ylabel("Elevation (mAHD)", fontsize=6)
        ax.tick_params(labelsize=6)
        fig.tight_layout()

        safe_var = var.replace(" ", "_").replace("[", "").replace("]", "").replace(".", "").replace("/", "")
        filename = f"{safe_var}_{campaign}.png"
        filepath = os.path.join(output_dir, filename)
        fig.savefig(filepath, dpi=300)
        plt.close(fig)
        print(f"  Saved: {filepath}")

print("\nDone.")
