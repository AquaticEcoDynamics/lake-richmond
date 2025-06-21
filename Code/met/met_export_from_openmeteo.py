import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import os  # ← Add this line


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": -32.2855846,
	"longitude": 115.7145707,
	"start_date": "1980-01-01",
	"end_date": "2023-12-31",
	"hourly": ["temperature_2m", "relative_humidity_2m", "rain", "cloud_cover", "wind_speed_10m", "shortwave_radiation", "terrestrial_radiation"],
	"models": "best_match",
	"timezone": "Asia/Singapore",
	"wind_speed_unit": "ms"
}

output_directory = "Data/data-warehouse/csv/openmeteo"
output_file_name = "openmeteo_hourly_1980-2024.csv"

os.makedirs(output_directory, exist_ok=True)

output_full_path = os.path.join(output_directory, output_file_name)

responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_rain = hourly.Variables(2).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()
hourly_shortwave_radiation = hourly.Variables(5).ValuesAsNumpy()
hourly_terrestrial_radiation = hourly.Variables(6).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["rain"] = hourly_rain
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
hourly_data["terrestrial_radiation"] = hourly_terrestrial_radiation

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Export the DataFrame to a CSV file
hourly_dataframe.to_csv(output_full_path, index=False)
print(f"Exported to {output_file_name}")