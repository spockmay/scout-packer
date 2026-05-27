import json
import urllib.request
from datetime import datetime

CATEGORIES = {
    0: "Essentials",
    1: "Shelter & Bedding",
    2: "Clothing",
    3: "Toiletries",
    4: "Tools",
    5: "Cooking",
    6: "Leisure",
}


class Equipment:
    def __init__(self, name: str, category: int) -> None:
        self.name = name
        self.category = category

    def _to_dict(self) -> dict:
        return {"name": self.name, "category": self.category}

    def __repr__(self) -> str:
        return json.dumps(self._to_dict())

    def __lt__(self, other):
        if self.category == other.category:
            return self.name < other.name
        return self.category < other.category


def generate_categorized_gear_dict(equipment_list):
    """
    Builds a dict where the keys are the equipment categories and the
    values are a list of equipment names. This is used to simplify the
    front-end rendering
    """
    sorted_equipment = sorted(equipment_list)

    # Initialize the dictionary using the string representations of the categories
    categorized_dict = {cat_name: [] for cat_name in CATEGORIES.values()}

    # Populate the dictionary with the equipment names
    for item in sorted_equipment:
        # Look up the string name using the item's integer category ID
        category_string = CATEGORIES.get(item.category)

        if category_string:
            categorized_dict[category_string].append(item.name)

    # Remove categories that don't have any items assigned to them
    categorized_dict = {k: v for k, v in categorized_dict.items() if v}

    return categorized_dict


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
            Equipment("Class A Uniform", 2),
            Equipment("Personal First Aid Kit", 0),
            Equipment("Extra Clothing", 0),
            Equipment("Filled Water Bottle", 0),
            Equipment("Flashlight or Headlamp", 0),
            Equipment("Map and compass", 0),
            Equipment("Insect repellant", 0),
            Equipment("Safety whistle", 0),
            Equipment("Sleeping Bag", 1),
            Equipment("Sleeping Pad", 1),
            Equipment("Pillow", 1),
            Equipment("PJs", 2),
            Equipment("Deodorant", 3),
            Equipment("Toothbrush", 3),
            Equipment("Toothpaste", 3),
            Equipment("Hair Brush", 3),
            Equipment("Shower Kit", 3),
            Equipment("Hand Sanitizer", 3),
            Equipment("Lip Balm", 3),
            Equipment("Books to read", 6),
            Equipment("Boots", 2),
            Equipment("Camp Shoes", 2),
            Equipment("Mess kit", 5),
            Equipment("Daypack", 0),
            Equipment("Trashbag", 0),
            Equipment("Towel", 3),
            Equipment("Camp Chair", 6),
        ]
        if query_params.get("fire", "true").lower() == "true":
            gear_list.append(Equipment("Fire Starter", 4))
            gear_list.append(Equipment("Tinder", 4))
        if query_params.get("knife", "true").lower() == "true":
            gear_list.append(Equipment("Pocketknife", 4))

        if query_params.get("camper", "scout") == "cub":
            gear_list.append(Equipment("Stuffed Animal", 1))
            gear_list.append(Equipment("Cub Scout Book", 0))
        elif query_params.get("camper", "scout") == "scout":
            gear_list.append(Equipment("Stuffed Animal", 1))
            gear_list.append(Equipment("Scout Book", 0))
            gear_list.append(Equipment("Toilet paper", 3))
        else:
            gear_list.append(Equipment("Toilet paper", 3))

        if trip_days > 0:
            gear_list.append(Equipment(f"Clothes ({trip_days_str})", 2))

        if max_precip_prob > 40:  # max chance of precip > 40%
            gear_list.append(Equipment("Rain Jacket/Poncho", 2))
            gear_list.append(Equipment("Extra socks", 2))
            conditions.append("rain")

        if min_apparent_temp < -10:
            gear_list.append(Equipment("Base Layers", 2))
            gear_list.append(Equipment("Hat & Mittens", 2))
            gear_list.append(Equipment("Wind-proof Outer Layers", 2))
            conditions.append("dangerous cold")
        elif min_apparent_temp < 7:  # lowest low is below 7C/45F
            gear_list.append(Equipment("Base Layers", 2))
            gear_list.append(Equipment("Hat & Gloves", 2))
            conditions.append("cold")

        if max_apparent_temp > 37:  # highest high is > 37C/100F
            gear_list.append(Equipment("Extra water", 0))
            gear_list.append(Equipment("Electrolyte packs", 0))
            conditions.append("dangerous hot")
        elif max_apparent_temp > 32:  # highest high is > 32C/90F
            gear_list.append(Equipment("Extra water", 0))
            gear_list.append(Equipment("Electrolyte packs", 0))
            conditions.append("hot")

        if max_uv > 6:
            gear_list.append(Equipment("SPF30+ Sunscreen", 0))
            gear_list.append(Equipment("Sun hat", 0))
            conditions.append("high uv")
        elif max_uv > 3:
            gear_list.append(Equipment("SPF30+ Sunscreen", 0))
            gear_list.append(Equipment("Sun hat", 0))

        if max_wind > 93:
            conditions.append("extreme wind hazard")
        elif max_wind > 64:
            gear_list.append(Equipment("Extra tent stakes", 0))
            conditions.append("wind hazard")
        elif max_wind > 41:
            gear_list.append(Equipment("Extra tent stakes", 0))
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
                    "recommended_gear": generate_categorized_gear_dict(
                        gear_list
                    ),
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
