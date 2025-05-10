import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()


def get_weather(location="Rawalpindi", days=1):
    """
    Get weather forecast for a specific location for the specified number of days.
    Uses a looping technique to bypass the API's limitation for forecasts beyond 3 days.

    Args:
        location (str): Location name (city, region, etc.)
        days (int): Number of forecast days (1-14)

    Returns:
        dict: Weather forecast data by date
    """
    api_key = os.environ.get("WEATHER_API_KEY")

    if days < 1:
        return {"error": "Days must be at least 1"}

    today = datetime.now()

    forecast_result = {}

    for i in range(days):
        current_date = today + timedelta(days=i)
        formatted_date = current_date.strftime("%Y-%m-%d")

        url = f"https://api.weatherapi.com/v1/forecast.json?q={location}&days=1&dt={formatted_date}&key={api_key}"

        response = requests.get(url)
        if response.status_code != 200:
            forecast_result[formatted_date] = {
                "error": f"API request failed with status code {response.status_code}"
            }
            continue

        data = response.json()

        if (
            "forecast" in data
            and "forecastday" in data["forecast"]
            and len(data["forecast"]["forecastday"]) > 0
        ):
            day_forecast = data["forecast"]["forecastday"][0]
            day_data = day_forecast["day"]

            max_temp_f = (day_data["maxtemp_c"] * 9 / 5) + 32
            min_temp_f = (day_data["mintemp_c"] * 9 / 5) + 32

            forecast_result[formatted_date] = {
                "Condition": day_data["condition"]["text"],
                "Max Temp": f"{day_data['maxtemp_c']}°C )",
                "Min Temp": f"{day_data['mintemp_c']}°C ",
                "Avg Temp": f"{day_data['avgtemp_c']}°C ",
                "Humidity": f"{day_data['avghumidity']}%",
                "Precipitation": f"{day_data['totalprecip_mm']} mm",
                "Wind": f"{day_data['maxwind_kph']} kph",
            }
        else:
            forecast_result[formatted_date] = {
                "error": "No forecast data available for this date"
            }

    return forecast_result


def get_current_weather_summary(location):
    """
    Get a simplified current weather summary for a location.

    Args:
        location (str): Location name (city, region, etc.)

    Returns:
        str: A brief summary of current weather conditions
    """
    weather_data = get_weather(location, 1)

    if "error" in weather_data or not weather_data:
        return "Weather data unavailable"

    current_date = next(iter(weather_data))
    current_weather = weather_data[current_date]

    return f"{current_weather['Condition']}, {current_weather['Avg Temp']}, {current_weather['Humidity']} humidity"


# if __name__ == "__main__":
#     # Example for 3-day forecast
#     weather_3_day = get_weather("Rawalpindi", 4)
#     print("=== 3-DAY FORECAST ===")
#     for date, day_weather in weather_3_day.items():
#         print(f"\n{date}")
#         for k, v in day_weather.items():
#             print(f"{k}: {v}")

#     # Example for 14-day forecast using the loop technique
#     weather_14_day = get_weather("Rawalpindi", 14)
#     print("\n\n=== 14-DAY FORECAST ===")
#     for date, day_weather in weather_14_day.items():
#         print(f"\n{date}")
#         for k, v in day_weather.items():
#             print(f"{k}: {v}")

#     # Example for current weather summary
#     print("\n\n=== CURRENT WEATHER SUMMARY ===")
#     print(get_current_weather_summary("Rawalpindi"))
