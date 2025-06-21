
# Import necessary libraries 
import pandas as pd
import matplotlib.pyplot as plt

# Re-define the file path after reset
excel_file = "../../Data/data-lake/MWH/MWH_DigitisedData.xlsx"

# Load the Excel file and the first sheet
xls_new = pd.ExcelFile(excel_file)
df_level = pd.read_excel(xls_new, sheet_name=0)

# Display the first few rows
df_level.head()

# Prepare both datetime series and corresponding elevation data
df_level['Datetime_1'] = pd.to_datetime(df_level['date'], errors='coerce')
df_level['Datetime_2'] = pd.to_datetime(df_level['date.1'], errors='coerce')

# Filter and prepare two data series for plotting
df1 = df_level[['Datetime_1', 'Stadia WL']].dropna()
df2 = df_level[['Datetime_2', 'WL Elevation']].dropna()

# Plot both time series
plt.figure(figsize=(12, 6))
plt.plot(df1['Datetime_1'], df1['Stadia WL'], label='Stadia WL', color='orange', marker='o', linestyle='None')
plt.plot(df2['Datetime_2'], df2['WL Elevation'], label='WL Elevation', color='blue', marker='x')
plt.xlabel("Date")
plt.ylabel("Water Level (m AHD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig('../../Data/data-lake/MWH/MWH_WL.png')
