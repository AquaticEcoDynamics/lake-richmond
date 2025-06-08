"""
Script: inspect_netcdf_structure.py

Description:
    This script opens a NetCDF file and prints metadata including dimensions,
    variables, global attributes, and coordinate axes to help understand its structure.

Requirements:
    - netCDF4
    - numpy

Author: Brendan Busch, Matthew Hipsey
"""

from netCDF4 import Dataset
import numpy as np
import os

# --- Path to NetCDF file ---
nc_path = "Working/BARRA/BARRA_SUB_19991001_20010101.nc"

# --- Open and inspect ---
if not os.path.exists(nc_path):
    print(f"⚠️ File not found: {nc_path}")
else:
    with Dataset(nc_path, 'r') as nc:
        print("✅ NetCDF file loaded.\n")
        print("🔹 Global Attributes:")
        for attr in nc.ncattrs():
            print(f"  {attr}: {getattr(nc, attr)}")

        print("\n🔹 Dimensions:")
        for dim_name, dim in nc.dimensions.items():
            print(f"  {dim_name}: {len(dim)}")

        print("\n🔹 Variables:")
        for var_name, var in nc.variables.items():
            shape = var.shape
            units = getattr(var, 'units', 'n/a')
            print(f"  {var_name} {shape} [units: {units}]")

        print("\n🔹 Sample time values (if present):")
        if "time" in nc.variables:
            time_vals = nc.variables["time"][:10]
            print(f"  First 10 time values: {time_vals}")

        print("\n🔹 Sample lat/lon values (if present):")
        if "latitude" in nc.variables:
            print(f"  Latitude sample: {nc.variables['latitude'][:5]}")
        elif "lat" in nc.variables:
            print(f"  Latitude sample: {nc.variables['lat'][:5]}")
        if "longitude" in nc.variables:
            print(f"  Longitude sample: {nc.variables['longitude'][:5]}")
        elif "lon" in nc.variables:
            print(f"  Longitude sample: {nc.variables['lon'][:5]}")