# Profiler Data Processing and Plotting

## Instrument

JFE Advantech AAQ-RINKO (AAQ-PRO2) water quality profiler. Profiles are collected at discrete sites along a north-south transect across Lake Richmond.

## Campaigns

| Campaign | Date | Sites | Surface Level (mAHD) |
|----------|------|-------|----------------------|
| 1 | 2025-03-22 | 15 (0a–10b) | 0.50 |
| 2 | 2025-05-09 | 12 (no 0c) | 0.48 |
| 3 | 2025-08-17 | 12 (no 0c) | 2.10 |
| 4 | 2025-10-18 | 12 (no 0c) | 1.80 |

## Input Files

### Index file
- **Path:** `Data/data-lake/UWA/index_march_2025.xlsx`
- Contains one row per site per campaign with columns: Campaign, Site ID, Lat, Long, Filename, Bottom Depth
- Site coordinates are in WGS84 (EPSG:4326)

### Profiler CSV files
- **Path:** `Data/data-lake/UWA/WQ profiling/FINAL/{campaign_date}/`
- Raw CSV exports from the AAQ-PRO2 instrument
- Most files have a 66-line instrument header terminated by a `[Item]` marker; data rows begin after this marker
- One exception: SITE6 (March) is a pre-processed file with no header — the script auto-detects this by searching for `[Item]`
- Encoding: latin-1 (UTF-8 µ character appears as `ï¿½` and is normalised to `u` in column names)
- Columns include: Depth [m], Temp. [degC], Sal., Cond. [mS/cm], EC25 [uS/cm], Density [kg/m3], Chl-Flu. [ppb], Chl-a [ug/l], Turb. [FTU], pH, ORP [mV], DO [%], DO [mg/l], Quant. [umol/(m2*s)]

## Scripts

All scripts are run from the project root directory (`lake-richmond/`).

### `plot_profiler_contours_mar_2025.py`
Original single-campaign script for the March 2025 data. Kept as reference.

### `plot_profiler_contours_2025.py`
Version 1 multi-campaign script. Uses `scipy.griddata` with linear interpolation. Vertical axis is depth below surface (m). Outputs to `Profiler/`.

### `plot_profiler_contours_2025_v2.py`
**Active** single-panel script. Uses two-step interpolation (see below) with mAHD vertical reference. Produces one PNG per variable per campaign. Outputs to `Profiler_v2/{campaign_date}/`.

### `plot_profiler_multipanel_2025.py`
Multi-panel comparison figures (A4 portrait, 4 rows x 2 columns). Each row is a campaign, each column is a variable. Outputs to `Profiler_v2/`.

Current pairings:
1. Temperature + Density
2. EC25 + Salinity
3. pH + Chlorophyll-a
4. DO (mg/L) + DO (%)

## Output Images

### Single-panel (`Profiler_v2/{campaign_date}/`)
- 13 PNGs per campaign (52 total), one per variable
- Format: `{Variable}_{campaign_date}.png` at 300 DPI

### Multi-panel (`Profiler_v2/`)
- `multipanel_TempdegC_Densitykgm3.png`
- `multipanel_EC25uScm_Sal.png`
- `multipanel_pH_Chl-augl.png`
- `multipanel_DOmgl_DO%.png`
- A4 width (8.27 in) x 10.69 in, 300 DPI

## Data Processing Assumptions

### Vertical reference frame
- All elevations are referenced to the Australian Height Datum (mAHD)
- Conversion: `elevation_mAHD = surface_level_mAHD - depth_below_surface`
- Surface level is set per campaign based on gauge data (see table above)

### Transect distance
- Site coordinates (WGS84) are projected to UTM Zone 50S (EPSG:32750)
- Cumulative Euclidean distance is calculated along the transect from north to south
- The March campaign (15 sites, best coverage) defines the reference x-axis range for all plots

### Interpolation method (two-step)
1. **Vertical interpolation:** Each profile is interpolated onto a common elevation grid (300 points) using `scipy.interp1d` (linear). This preserves the vertical structure of each profile.
2. **Horizontal interpolation:** At each elevation level, values are interpolated across the transect distance (300 points) using `scipy.interp1d` (linear).

This two-step approach is preferred over direct 2D griddata for profiler transect data because it respects the anisotropic nature of the measurements (high vertical resolution, sparse horizontal spacing).

### Extrapolation
- **Upward:** Each profile is extended from its shallowest measurement to the water surface by holding the shallowest measured value constant. This prevents artificial "bending" of contours near the surface.
- **Downward:** Each profile is extended below its deepest measurement by 50% of the gap between its maximum depth and the overall transect maximum depth. The deepest measured value is held constant. This fills gaps at deeper sites without over-extrapolating.

### Bottom clipping
- For pH and Chl-a, the bottom 0.5 m of each profile is removed before interpolation. This removes sensor artefacts (e.g., sediment disturbance, optical interference) that produce unreliable readings near the lake bed.

### Bathymetry mask
- The grey bottom mask uses bottom depths from the March 2025 campaign (reference campaign with the most sites), interpolated across the full transect distance. This provides a consistent bathymetric reference across all campaigns regardless of which sites were sampled.

### Reference elevation line
- A dashed grey line at 0.6 mAHD is shown on all plots, representing a reference water level.

### Buffer sites
- The first 2 and last 2 sites along the transect are excluded from site marker annotations to reduce label clutter at the transect edges. Data from these sites is still used in the interpolation.
