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

Run with:
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
site_refs = ['All'] + sorted(df['Site Ref'].dropna().unique())
variable_names = ['All'] + sorted(df['Variable Name'].dropna().unique())

selected_site_ref = st.sidebar.selectbox("Site Ref", site_refs)
selected_variable = st.sidebar.selectbox("Variable Name", variable_names)

if selected_site_ref != 'All':
    df = df[df['Site Ref'] == selected_site_ref]
if selected_variable != 'All':
    df = df[df['Variable Name'] == selected_variable]

filtered = df

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
st.subheader(f"📄 Data for Site: {selected_site_ref if selected_site_ref != 'All' else 'All Sites'}")
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
if {'Latitude', 'Longitude'}.issubset(filtered.columns):
    st.subheader("🗺 Sampling Locations Map")
    map_df = filtered[['Latitude', 'Longitude']].dropna().rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
    st.map(map_df)