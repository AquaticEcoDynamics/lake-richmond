import pandas as pd
import os

variable_map = {
    "Temp": {"label": "Temperature (°C)", "clean_name": "Temperature"},
    "EC": {"label": "Electrical Conductivity (µS/cm)", "clean_name": "Electrical_Conductivity"}  # originally in mS/cm, converted
}

file_path = "Data/data-lake/HGE/2018/Copy of Richmond 01.xlsx"
sheet_name = "EC and Temp"

# Load additional data from "Point Hydro Data" sheet
sheet_name_phd = "Point Hydro Data"
df_phd = pd.read_excel(file_path, sheet_name=sheet_name_phd, header=None)

# Site MW
df_mw = pd.DataFrame({
    "Date": pd.to_datetime(df_phd.loc[2:4, 0]),
    "EC": df_phd.loc[2:4, 2].astype(float) * 1000,  # mS/cm to µS/cm
    "Temp": pd.NA
})
df_mw["Agency"] = "HGE"
df_mw["Site"] = "Barod (2018)"

# Site RV
df_rv = pd.DataFrame({
    "Date": pd.to_datetime(df_phd.loc[2:4, 0]),
    "EC": df_phd.loc[2:4, 4].astype(float) * 1000,  # mS/cm to µS/cm
    "Temp": df_phd.loc[2:4, 6].astype(float)
})
df_rv["Agency"] = "HGE"
df_rv["Site"] = "Board (2018)"

# Append MW and RV data to corresponding parquet files
for df_site in [df_mw, df_rv]:
    for var in ["Temp", "EC"]:
        if var in df_site.columns and not df_site[var].isna().all():
            var_label = variable_map[var]["label"]
            var_clean_name = variable_map[var]["clean_name"]
            df_var = pd.DataFrame({
                "DateTime": df_site["Date"],
                "Reading": df_site[var],
                "Agency": df_site["Agency"],
                "Site": df_site["Site"],
                "Variable": var_label
            })

            parquet_path = f"Data/data-warehouse/parquet/WQ/{var_clean_name}.parquet"
            if os.path.exists(parquet_path):
                existing_df = pd.read_parquet(parquet_path)
                combined_df = pd.concat([existing_df, df_var], ignore_index=True)
                combined_df.drop_duplicates(subset=["DateTime", "Agency", "Site", "Variable"], inplace=True)
                combined_df.to_parquet(parquet_path, index=False)
            else:
                df_var.to_parquet(parquet_path, index=False)

df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=["Date/time", "Temperature[°C]", "Conductivity[mS/cm]"])

df.columns = ["Date", "Temp", "EC"]

df["EC"] = df["EC"] * 1000  # Convert from mS/cm to µS/cm
df["Date"] = pd.to_datetime(df["Date"])

agency = "HGE"
site = "Logger (2018)"

for var in ["Temp", "EC"]:
    var_label = variable_map[var]["label"]
    var_clean_name = variable_map[var]["clean_name"]
    df_var = pd.DataFrame({
        "DateTime": df["Date"],
        "Reading": df[var],
        "Agency": agency,
        "Site": site,
        "Variable": var_label
    })

    parquet_path = f"Data/data-warehouse/parquet/WQ/{var_clean_name}.parquet"
    if os.path.exists(parquet_path):
        existing_df = pd.read_parquet(parquet_path)
        combined_df = pd.concat([existing_df, df_var], ignore_index=True)
        combined_df.drop_duplicates(subset=["DateTime", "Agency", "Site", "Variable"], inplace=True)
        combined_df.to_parquet(parquet_path, index=False)
    else:
        df_var.to_parquet(parquet_path, index=False)
