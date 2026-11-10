import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city):
    city = (city or "").strip()
    if not city:
        return {"error": "Please enter a city name."}
    geo_response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=15,
    )
    geo_response.raise_for_status()
    places = geo_response.json().get("results", [])
    if not places:
        return {"error": "City not found. Try another city name."}
    place = places[0]
    weather_response = requests.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": 3,
            "timezone": "auto",
        },
        timeout=15,
    )
    weather_response.raise_for_status()
    data = weather_response.json()
    return {
        "location": ", ".join(x for x in [place.get("name"), place.get("admin1"), place.get("country")] if x),
        "current": data.get("current", {}),
        "daily": data.get("daily", {}),
    }
