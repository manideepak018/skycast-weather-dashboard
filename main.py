
import requests

city = input("Enter city name: ").strip()

geo_url = "https://geocoding-api.open-meteo.com/v1/search"
geo_params = {
    "name": city,
    "count": 1,
    "language": "en"
}

geo_response = requests.get(
    geo_url, params=geo_params, timeout=15
)
geo_response.raise_for_status()

results = geo_response.json().get("results", [])

if not results:
    print("City not found.")
else:
    location = results[0]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    response = requests.get(
        weather_url, params=weather_params, timeout=15
    )
    response.raise_for_status()

    data = response.json()
    current = data["current"]
    units = data["current_units"]

    print("\n===== WEATHER REPORT =====")
    print("Location:", location["name"], location.get("country", ""))
    print("Temperature:", current["temperature_2m"], units["temperature_2m"])
    print("Humidity:", current["relative_humidity_2m"], units["relative_humidity_2m"])
    print("Wind Speed:", current["wind_speed_10m"], units["wind_speed_10m"])
    print("Local Time:", current["time"])
