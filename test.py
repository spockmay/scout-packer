import json
import urllib.request
from datetime import datetime

weather_url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&daily=apparent_temperature_max,apparent_temperature_min,uv_index_max,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max&start_date=2026-04-23&end_date=2026-05-07"
with urllib.request.urlopen(weather_url) as response:
    weather_data = json.loads(response.read().decode())

# 2. Extract data for the days selected
daily = weather_data.get("daily", {})
max_apparent_temp = max(daily.get("apparent_temperature_max", []))
min_apparent_temp = min(daily.get("apparent_temperature_min", []))
max_uv = max(daily.get("uv_index_max", []))
max_precip_prob = max(daily.get("precipitation_probability_max", []))
max_wind = max(daily.get("wind_speed_10m_max", []))
max_gust = max(daily.get("wind_gusts_10m_max", []))

print(max_apparent_temp)
print(min_apparent_temp)
print(max_uv)
print(max_precip_prob)
print(max_wind)
print(max_gust)
