import json
import urllib.request
from datetime import datetime


def handler(event, context):
    # 1. Log the full event so you can see exactly what AWS sees in CloudWatch
    # print(f"FULL EVENT RECEIVED: {json.dumps(event)}")

    # 2. Extract parameters with safe defaults
    query_params = event.get("queryStringParameters", {})

    # If queryStringParameters is None (sometimes happens with certain request types)
    if not query_params:
        query_params = {}

    lat = query_params.get("lat", "41.44")
    lon = query_params.get("lon", "-81.33")
    start_date_str = query_params.get("date")  # "YYYY-MM-DD"
    end_date_str = query_params.get("enddate")  # "YYYY-MM-DD"

    # print(f"USING COORDINATES: {lat}, {lon}")

    # The weather API now uses the dynamic coordinates
    query = "daily=apparent_temperature_max,apparent_temperature_min,uv_index_max,precipitation_probability_max,wind_speed_10m_max"
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&{query}&timezone=auto&start_date={start_date_str}&end_date={end_date_str}"

    try:
        # Using standard urllib to keep the Lambda 'slim' (no extra dependencies)
        with urllib.request.urlopen(weather_url) as response:
            weather_data = json.loads(response.read().decode())

        # 2. Extract data for the days selected
        daily = weather_data.get("daily", {})
        max_apparent_temp = max(daily.get("apparent_temperature_max", []))
        min_apparent_temp = min(daily.get("apparent_temperature_min", []))
        max_uv = max(daily.get("uv_index_max", []))
        max_precip_prob = max(daily.get("precipitation_probability_max", []))
        max_wind = max(daily.get("wind_speed_10m_max", []))

        conditions = []

        gear_list = [
            "Class A Uniform",
            "Pocketknife",
            "Personal First Aid Kit",
            "Extra Clothing",
            "Filled Water Bottle",
            "Flashlight or Headlamp",
            "Fire Starter",
            "Sun Protection",
            "Map and compass",
            "Insect repellant",
            "Safety whistle",
            "Toilet paper",
            "Sleeping Bag",
            "Sleeping pad",
            "Pillow",
            "Clothes",
            "PJs",
            "Toiletries",
            "Books to read",
            "Boots",
            "Camp Shoes",
            "Mess kit",
            "Scout Book",
            "Daypack",
            "Trashbag",
            "Towel",
            "Stuffed Animal",
            "Camp Chair",
        ]

        if max_precip_prob > 40:  # max chance of precip > 40%
            gear_list.append("Rain Jacket/Poncho")
            gear_list.append("Extra socks")
            conditions.append("rain")

        if min_apparent_temp < 7:  # lowest low is below 7C/45F
            gear_list.append("Base Layers")
            gear_list.append("Hat & Gloves")
            conditions.append("cold")

        if min_apparent_temp < -10:
            conditions.append("dangerous cold")

        if max_apparent_temp > 32:  # highest high is > 32C/90F
            gear_list.append("Extra water")
            gear_list.append("Electrolyte packs")
            conditions.append("hot")

        if max_apparent_temp > 37:  # highest high is > 37C/100F
            conditions.append("dangerous hot")

        if max_uv > 3:
            gear_list.append("SPF30+ Sunscreen")
            gear_list.append("Sun hat")

        if max_uv > 6:
            conditions.append("high uv")

        if max_wind > 41:
            gear_list.append("Extra tent stakes")
            conditions.append("wind warning")

        if max_wind > 64:
            conditions.append("wind hazard")

        if max_wind > 93:
            conditions.append("extreme wind hazard")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "location": f"{lat}, {lon}",
                    "precip_prob": f"{max_precip_prob}%",
                    "recommended_gear": gear_list,
                    "conditions": conditions,
                    "date": start_date_str,
                },
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
