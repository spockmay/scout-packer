import json
import urllib.request
from datetime import datetime


def calculate_trip_days(start_str, end_str):
    """
    Computes the number of days between two 'YYYY-MM-DD' strings.
    Example: '2026-06-12' to '2026-06-14' returns 2. We don't need
             to pack a set of clothes for day 1, we are wearing them!
    """
    try:
        # Convert strings to datetime objects
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")

        # Calculate the difference (returns a timedelta object)
        delta = end_date - start_date

        return delta.days

    except ValueError as e:
        # Log error for system monitoring
        print(f"Date parsing error: {e}")
        return 0


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

    trip_days = calculate_trip_days(start_date_str, end_date_str)
    if trip_days == 1:
        trip_days_str = f"{trip_days} day"
    else:
        trip_days_str = f"{trip_days} days"

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
            "Personal First Aid Kit",
            "Extra Clothing",
            "Filled Water Bottle",
            "Flashlight or Headlamp",
            "Sun Protection",
            "Map and compass",
            "Insect repellant",
            "Safety whistle",
            "Sleeping Bag",
            "Sleeping pad",
            "Pillow",
            "PJs",
            "Toiletries",
            "Books to read",
            "Boots",
            "Camp Shoes",
            "Mess kit",
            "Daypack",
            "Trashbag",
            "Towel",
            "Camp Chair",
        ]

        if query_params.get("fire", "true").lower() == "true":
            gear_list.append("Fire Starter")
        if query_params.get("knife", "true").lower() == "true":
            gear_list.append("Pocketknife")

        if query_params.get("camper", "scout") == "cub":
            gear_list.append("Stuffed Animal")
            gear_list.append("Cub Scout Book")
        elif query_params.get("camper", "scout") == "scout":
            gear_list.append("Stuffed Animal")
            gear_list.append("Scout Book")
            gear_list.append("Toilet paper")
        else:
            gear_list.append("Toilet paper")

        if trip_days > 0:
            gear_list.append(f"Clothes ({trip_days_str})")

        if max_precip_prob > 40:  # max chance of precip > 40%
            gear_list.append("Rain Jacket/Poncho")
            gear_list.append("Extra socks")
            conditions.append("rain")

        if min_apparent_temp < -10:
            gear_list.append("Base Layers")
            gear_list.append("Hat & Mittens")
            gear_list.append("Wind-proof Outer Layers")
            conditions.append("dangerous cold")
        elif min_apparent_temp < 7:  # lowest low is below 7C/45F
            gear_list.append("Base Layers")
            gear_list.append("Hat & Gloves")
            conditions.append("cold")

        if max_apparent_temp > 37:  # highest high is > 37C/100F
            gear_list.append("Extra water")
            gear_list.append("Electrolyte packs")
            conditions.append("dangerous hot")
        elif max_apparent_temp > 32:  # highest high is > 32C/90F
            gear_list.append("Extra water")
            gear_list.append("Electrolyte packs")
            conditions.append("hot")

        if max_uv > 6:
            gear_list.append("SPF30+ Sunscreen")
            gear_list.append("Sun hat")
            conditions.append("high uv")
        elif max_uv > 3:
            gear_list.append("SPF30+ Sunscreen")
            gear_list.append("Sun hat")

        if max_wind > 93:
            conditions.append("extreme wind hazard")
        elif max_wind > 64:
            gear_list.append("Extra tent stakes")
            conditions.append("wind hazard")
        elif max_wind > 41:
            gear_list.append("Extra tent stakes")
            conditions.append("wind warning")

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
                    "forecast_url": f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}",
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
