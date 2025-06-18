import pandas as pd

# Define the file path
file_path = "../../Data/data-lake/360E/4713AA_Rev 2 Lake Richmond Monitoring field & lab data.xlsx"

# Load the 'Data Logger' sheet
df_logger = pd.read_excel(file_path, sheet_name='Data Logger')

# Optional: combine Date and Time columns into a single datetime column
df_logger['Datetime'] = pd.to_datetime(df_logger['Date'].astype(str) + ' ' + df_logger['Time'].astype(str))

# Display first few rows
print(df_logger.head())

import matplotlib.pyplot as plt

# Plotting selected parameters
fig, axs = plt.subplots(5, 1, figsize=(12, 14), sharex=True)

# Conductivity
axs[0].plot(df_logger['Datetime'], df_logger['Pressure (HPa)'], color='black')
axs[0].set_ylabel("Pressure (HPa)")
axs[0].set_title("Lake Richmond 360E Data Logger Readings")

# Conductivity
axs[1].plot(df_logger['Datetime'], df_logger['Measured Conductivity (µS/cm)'])
axs[1].set_ylabel("Conductivity (µS/cm)")

# Temperature
axs[2].plot(df_logger['Datetime'], df_logger['Temperature (°C)'], color='orange')
axs[2].set_ylabel("Temperature (°C)")

# TDS
axs[3].plot(df_logger['Datetime'], df_logger['TDS (mg/L)'], color='green')
axs[3].set_ylabel("TDS (mg/L)")

# Salinity
axs[4].plot(df_logger['Datetime'], df_logger['Measured Salinity (PSU)'], color='red')
axs[4].set_ylabel("Salinity (PSU)")
axs[4].set_xlabel("Date")

plt.tight_layout()
plt.show()

plt.savefig('../../Data/data-lake/360E/360E.png')
