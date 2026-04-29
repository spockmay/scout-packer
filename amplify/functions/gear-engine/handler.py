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
    selected_date_str = query_params.get("date")  # "YYYY-MM-DD"

    # print(f"USING COORDINATES: {lat}, {lon}")

    # 1. Determine the 'Day Index'
    day_index = 0
    if selected_date_str:
        try:
            today = datetime.now().date()
            selected_date = datetime.strptime(
                selected_date_str, "%Y-%m-%d"
            ).date()
            # Calculate the difference in days
            day_index = (selected_date - today).days

            # Open-Meteo free tier usually gives 7-14 days.
            # We should bound this to prevent IndexErrors.
            day_index = max(0, min(day_index, 6))
        except Exception:
            day_index = 0

    # The weather API now uses the dynamic coordinates
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    try:
        # Using standard urllib to keep the Lambda 'slim' (no extra dependencies)
        with urllib.request.urlopen(weather_url) as response:
            weather_data = json.loads(response.read().decode())

        # 2. Extract data for the SPECIFIC day selected
        daily = weather_data.get("daily", {})
        precip_sum = daily.get("precipitation_sum", [0])[day_index]
        temp_min = daily.get("temperature_2m_min", [50])[day_index]
        temp_max = daily.get("temperature_2m_max", [70])[day_index]

        gear_list = [
            "Standard Uniform",
            "Water Bottle",
            "Personal First Aid Kit",
        ]

        if precip_sum > 0:
            gear_list.append("Rain Jacket/Poncho")
            gear_list.append("Pack Cover")

        if temp_min < 50:  # Standard Scout 'Cold Weather' threshold
            gear_list.append("Warm Layers (Fleece/Wool)")
            gear_list.append("Sleeping Bag Liner")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "location": "%s, %s" % (lat, lon),
                    "forecast_precip": f"{precip_sum}mm",
                    "recommended_gear": gear_list,
                }
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
