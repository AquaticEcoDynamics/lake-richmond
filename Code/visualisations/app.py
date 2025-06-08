"""
App: app.py

Description:
This Streamlit dashboard provides an interactive interface for visualising water level
data extracted from merged Excel files and saved in a Parquet format. It allows users to:
- Select a monitoring site
- Filter by collection date range
- View summary statistics for readings
- Explore reading distributions and yearly trends
- Optionally display site locations on a map (if coordinates are available)

Inputs:
- combined_water_levels.parquet : A cleaned Parquet dataset containing water level data

Features:
- Site-based filtering
- Date range filtering
- Reading value distribution charts
- Yearly average trend analysis
- Optional geospatial site display via pydeck

Requirements:
- streamlit
- pandas
- pyarrow
- pydeck (optional map support)

Run with (local):
    streamlit run Code/visualisations/app.py --server.port 8501 
Run with (github codespaces):
    streamlit run Code/visualisations/app.py --server.port 8501 --server.address 0.0.0.0
View with (local):
    http://localhost:8501

Author: Brendan Busch, Matthew Hipsey
"""


import streamlit as st
import pandas as pd
import pydeck as pdk

# Load parquet data
@st.cache_data
def load_data():
    df = pd.read_parquet("Data/data-warehouse/parquet/DWER/combined_water_levels.parquet")
    # Parse datetime if needed
    if 'Collected Date Time' in df.columns:
        df['Collected Date Time'] = pd.to_datetime(df['Collected Date Time'], errors='coerce')
    return df

df = load_data()

# Global filters
st.sidebar.header("🔍 Global Filters")

# Dropdown for Variable Name
variable_options = sorted(df['Variable Name'].dropna().unique())
selected_variable = st.sidebar.selectbox("Select Variable Name", options=variable_options)

# Apply filter
filtered = df[df['Variable Name'] == selected_variable]

# Title
st.title("💧 Water Levels Dashboard")

# Optional date filter
if 'Collected Date Time' in filtered.columns:
    st.subheader("📅 Filter by Date Range")
    min_date = filtered['Collected Date Time'].min()
    max_date = filtered['Collected Date Time'].max()
    date_range = st.date_input("Date Range", [min_date, max_date])

    filtered = filtered[
        (filtered['Collected Date Time'] >= pd.to_datetime(date_range[0])) &
        (filtered['Collected Date Time'] <= pd.to_datetime(date_range[1]))
    ]

# Show filtered data table
st.subheader("📄 Data for Selected Variable")
st.dataframe(filtered)

# Summary stats
st.subheader("📊 Summary Statistics")
if 'Reading Value (Clean)' in filtered.columns:
    st.metric("Min", f"{filtered['Reading Value (Clean)'].min():.3f}")
    st.metric("Max", f"{filtered['Reading Value (Clean)'].max():.3f}")
    st.metric("Mean", f"{filtered['Reading Value (Clean)'].mean():.3f}")

# Distribution chart
st.subheader("📈 Reading Value Distribution")
if 'Reading Value (Clean)' in filtered.columns:
    st.bar_chart(filtered['Reading Value (Clean)'].dropna())

# Yearly aggregation
if 'Collected Date Time' in filtered.columns:
    filtered['Year'] = filtered['Collected Date Time'].dt.year
    yearly_avg = filtered.groupby('Year')['Reading Value (Clean)'].mean().dropna()
    if not yearly_avg.empty:
        st.subheader("📅 Yearly Average Readings")
        st.bar_chart(yearly_avg)

# Optional map
if {'Latitude', 'Longitude', 'Site Ref'}.issubset(filtered.columns):
    st.subheader("🗺 Sampling Locations Map")

    # Prepare map data
    map_df = filtered[['Site Ref', 'Latitude', 'Longitude']].dropna()
    map_df = map_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})

    # Diagnostic output
    st.caption(f"🧭 Map points available: {len(map_df)}")
    if map_df.empty:
        st.info("No site location data available for the selected variable.")
    else:
        st.dataframe(map_df[['Site Ref', 'lat', 'lon']])
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_color='[0, 0, 255]',
            get_radius=60,
            pickable=True,
        )

        tooltip = {"html": "<b>Site Ref:</b> {Site Ref}", "style": {"backgroundColor": "white", "color": "black"}}

        # Adjust map zoom and center based on data bounds
        lat_center = map_df["lat"].mean()
        lon_center = map_df["lon"].mean()
        lat_range = map_df["lat"].max() - map_df["lat"].min()
        lon_range = map_df["lon"].max() - map_df["lon"].min()
        max_range = max(lat_range, lon_range)
        zoom_level = 7 if max_range < 1 else 6 if max_range < 2 else 5 if max_range < 5 else 4

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=lat_center,
                longitude=lon_center,
                zoom=zoom_level,
                pitch=0,
            ),
            layers=[layer],
            tooltip=tooltip
        ))