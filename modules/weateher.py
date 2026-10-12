"""
Weather lookups via the OpenWeatherMap "current weather" endpoint.
"""

import requests

from config import OPENWEATHER_API_KEY, DEFAULT_CITY, TEMP_UNITS

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = None) -> str:
    """Return a spoken-friendly weather summary for the given city."""
    if not OPENWEATHER_API_KEY:
        return (
            "I can't check the weather yet because no OpenWeatherMap API key "
            "is configured. Add one to config.py or the OPENWEATHER_API_KEY "
            "environment variable."
        )

    city = city or DEFAULT_CITY
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": TEMP_UNITS,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        return f"I couldn't reach the weather service: {e}"

    if response.status_code == 404:
        return f"I couldn't find a place called {city}."
    if response.status_code != 200:
        return "The weather service returned an error, please try again later."

    data = response.json()
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    unit_label = "degrees Celsius" if TEMP_UNITS == "metric" else "degrees Fahrenheit"

    return (
        f"It's currently {temp:.0f} {unit_label} in {city.title()}, "
        f"with {description}. It feels like {feels_like:.0f} {unit_label}, "
        f"and humidity is at {humidity} percent."
    )