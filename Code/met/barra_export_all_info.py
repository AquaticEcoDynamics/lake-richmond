import os
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
from datetime import datetime

# --- Settings ---
data_dir = "Working/BARRA"
output_dir = "Data/data-warehouse/csv/barra"
os.makedirs(output_dir, exist_ok=True)

lat_target = -32.2855846
lon_target = 115.7145707

variables = [
    "uwnd10m", "vwnd10m", "mslp", "downward_longwave", "downward_shortwave",
    "air_temp_2m", "precip_rate", "relhum"
]

years = range(2000, 2013)  # inclusive

# --- Loop over years ---
for year in years:
    fname = [f for f in os.listdir(data_dir) if str(year) in f and f.endswith(".nc")]
    if not fname:
        print(f"⚠️ No file found for {year}")
        continue

    path = os.path.join(data_dir, fname[0])
    print(f"📂 Processing: {fname[0]}")

    with Dataset(path, "r") as nc:
        lats = nc.variables["latitude"][:]
        lons = nc.variables["longitude"][:]
        
        # --- Find nearest grid cell ---
        lat_idx = (np.abs(lats - lat_target)).argmin()
        lon_idx = (np.abs(lons - lon_target)).argmin()

        # --- Extract time values ---
        time_var = nc.variables["time"]
        times = num2date(time_var[:], units=time_var.units, only_use_cftime_datetimes=False)
        timestamps = [t.strftime("%Y-%m-%d %H:%M:%S") for t in times]

        # --- Extract variable time series at grid point ---
        data = {"time": timestamps}
        for var in variables:
            data[var] = nc.variables[var][:, lat_idx, lon_idx]

        # --- Save to CSV ---
        df = pd.DataFrame(data)
        out_csv = os.path.join(output_dir, f"BARRA_{year}_point.csv")
        df.to_csv(out_csv, index=False)
        print(f"✅ Saved: {out_csv}")