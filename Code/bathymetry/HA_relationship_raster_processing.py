"""
Script: calc_area_from_raster.py

Description:
    This script reads a bathymetric GeoTIFF and calculates the cumulative area 
    below specified elevation thresholds. It is designed to support height–area 
    analysis for lake and estuary bathymetry models.

Key Features:
    - Loads a GeoTIFF elevation raster
    - Defines elevation breakpoints from -14 m to +1 m in 0.5 m steps
    - Counts the number of cells at or below each elevation
    - Multiplies cell counts by the fixed raster cell area (2x2m = 4 m²)
    - Prints a height–area curve suitable for integration with lake volume models

Requirements:
    - numpy
    - rasterio

Author: Brendan Busch, Matthew Hipsey
"""

import numpy as np
import rasterio

# --- Parameters ---
tiff_path = "GIS/Bathymetry/Bathymetry_Interpolated_Clipped.tif"  # Update this path as needed
cell_area = 1.0  # m² per raster cell (2m x 2m)

# --- Load raster ---
with rasterio.open(tiff_path) as src:
    raster = src.read(1).astype(np.float32)
    raster[raster == src.nodata] = np.nan  # Replace NoData with NaN

# --- Define elevation levels ---
levels = np.arange(-14, 2.5, 0.5)  # -14 to 1 inclusive
cumulative_areas = []

# --- Calculate cumulative areas ---
for level in levels:
    mask = raster <= level
    count = np.count_nonzero(mask)
    area = count * cell_area
    cumulative_areas.append(area)

# --- Output results ---
print("Elevation (m)\tCumulative Area (m²)")
for level, area in zip(levels, cumulative_areas):
    print(f"{level:.1f}\t\t{area:.2f}")