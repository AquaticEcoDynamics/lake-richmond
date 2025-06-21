import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os


# Config section

# Plot x-axis limits
xlim_start = pd.Timestamp("2010-01-01")
xlim_end = pd.Timestamp("2015-01-01")

# Plot styles by site
plot_styles = {
    "s6142501": {"kind": "line", "color": "blue"},
    "Stadia": {"kind": "scatter", "color": "orange"},
    "WL": {"kind": "scatter", "color": "black"},
}

# Interval for X Ticks (yearly)
xtickint = 1

# Define the path to the parquet file
datapath = "Data/data-warehouse/parquet/level"
parquet_file = os.path.join(datapath, "lakelevel.parquet")

# Load the data
df = pd.read_parquet(parquet_file)


unique_sites = df["Site"].unique()
print("Sites in the dataset:", unique_sites)

# Create the plot
plt.figure(figsize=(12, 6))

# Plot each site separately with style
for site in df["Site"].unique():
    site_df = df[df["Site"] == site]
    label = f"{site_df['Agency'].iloc[0]} - {site}"
    style = plot_styles.get(site, {"kind": "line", "color": "gray"})
    if style["kind"] == "line":
        plt.plot(site_df["DateTime"], site_df["Reading"], label=label, color=style["color"])
    elif style["kind"] == "scatter":
        plt.scatter(site_df["DateTime"], site_df["Reading"], label=label, color=style["color"], s=10)

# Format the plot
plt.xlabel("Year")
plt.ylabel("Water Level (mAHD)")
plt.title("Lake Level Time Series")
plt.grid(True)

# Format x-axis ticks
locator = mdates.YearLocator(xtickint)
formatter = mdates.DateFormatter('%Y')
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)
plt.xlim(xlim_start, xlim_end)

plt.legend()
plt.tight_layout()
plt.show()