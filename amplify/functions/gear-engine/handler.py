import json
import urllib.request


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

    # print(f"USING COORDINATES: {lat}, {lon}")

    # The weather API now uses the dynamic coordinates
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    try:
        # Using standard urllib to keep the Lambda 'slim' (no extra dependencies)
        with urllib.request.urlopen(weather_url) as response:
            weather_data = json.loads(response.read().decode())

        # Simple Logic: If precipitation is predicted, add Rain Gear
        precip_sum = weather_data["daily"]["precipitation_sum"][0]
        temp_min = weather_data["daily"]["temperature_2m_min"][0]

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
