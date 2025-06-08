# pip install geopandas

"""
Script: contour_area_analysis.py

Description:
This script reads a shapefile containing 3D contour lines and calculates the cumulative surface area
at or below specified elevation levels. The analysis is performed in 0.5-meter increments, starting 
from -14 meters. It uses GeoPandas to process the spatial data and approximates closed regions from 
contour lines using small buffers, then calculates 2D area using unioned geometries.

Inputs:
- Shapefile: 'GIS/Bathymetry/LR_Topography_2m.shp' containing contour lines with elevation values.

Outputs:
- A table (DataFrame) of elevation vs. cumulative area (in square meters).

Intended Use:
- To estimate bathymetric surface area coverage at various depths, which can support volume 
  calculations, ecological assessments, or hydrodynamic modeling.

Requirements:
- geopandas
- pandas
- numpy
- shapely

Author: Brendan Busch, Matthew Hipsey

"""
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.ops import unary_union
from shapely.geometry import Polygon


# Load the shapefile
gdf = gpd.read_file('GIS/Bathymetry/TDB/1m_bathy_interp_contour_v2.shp')

# Drop features without contour data
gdf = gdf[gdf['Contour'].notnull()]
gdf['Contour'] = gdf['Contour'].astype(float)

# Optional: filter to reasonable contour range
min_elev = -14
max_elev = gdf['Contour'].max()
step = 0.5

# Generate contour steps
levels = np.arange(min_elev, max_elev + step, step)

# Container for results
results = []

for level in levels:
    # Get all lines at or below the current level
    level_gdf = gdf[gdf['Contour'] <= level]
    
    # Try to build polygons (requires lines to form closed loops)
    # Buffer by a very small value to help close the shapes
    buffered = level_gdf.geometry.buffer(0.1)  # adjust if needed
    unioned = unary_union(buffered)
    
    if unioned.is_empty:
        area = 0.0
    elif unioned.geom_type == 'Polygon':
        area = unioned.area
    elif unioned.geom_type == 'MultiPolygon':
        area = sum(p.area for p in unioned.geoms)
    else:
        area = 0.0

    results.append({'Height_m': level, 'Area_m2': area})

# Create a DataFrame
area_df = pd.DataFrame(results)

# Display the table
print(area_df)

