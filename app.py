
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city):
    # Step 1: Convert city name into coordinates
    geo_params = {
        "name": city,
        "count": 1,
        "language": "en"
    }

    geo_response = requests.get(
        GEOCODING_URL,
        params=geo_params,
        timeout=15
    )
    geo_response.raise_for_status()

    geo_data = geo_response.json()
    results = geo_data.get("results", [])

    if not results:
        return None

    location = results[0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Step 2: Fetch current weather
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "weather_code,"
            "is_day"
        ),
        "timezone": "auto"
    }

    weather_response = requests.get(
        WEATHER_URL,
        params=weather_params,
        timeout=15
    )
    weather_response.raise_for_status()

    weather_data = weather_response.json()
    current = weather_data["current"]
    units = weather_data["current_units"]

    # Step 3: Select an icon using the weather code
    code = current["weather_code"]
    is_day = current["is_day"]

    if code == 0:
        icon = "☀️" if is_day else "🌙"
        condition = "Clear sky"
    elif code in (1, 2):
        icon = "🌤️" if is_day else "☁️"
        condition = "Mainly clear or partly cloudy"
    elif code == 3:
        icon = "☁️"
        condition = "Overcast"
    elif code in (45, 48):
        icon = "🌫️"
        condition = "Foggy"
    elif code in (51, 53, 55, 56, 57):
        icon = "🌦️"
        condition = "Drizzle"
    elif code in (61, 63, 65, 66, 67, 80, 81, 82):
        icon = "🌧️"
        condition = "Rain"
    elif code in (71, 73, 75, 77, 85, 86):
        icon = "❄️"
        condition = "Snow"
    elif code in (95, 96, 99):
        icon = "⛈️"
        condition = "Thunderstorm"
    else:
        icon = "🌡️"
        condition = "Current conditions"

    # Step 4: Return values for the HTML template
    return {
        "city": location["name"],
        "country": location.get("country", ""),
        "temperature": current["temperature_2m"],
        "temperature_unit": units["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "humidity_unit": units["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "wind_unit": units["wind_speed_10m"],
        "time": current["time"],
        "icon": icon,
        "condition": condition
    }


@app.route("/", methods=["GET"])
def home():
    city = request.args.get("city", "").strip()
    weather = None
    error = None

    if city:
        try:
            weather = get_weather(city)

            if weather is None:
                error = (
                    "City not found. Check the spelling "
                    "and try again."
                )

        except requests.RequestException:
            error = (
                "Could not connect to the weather service. "
                "Check your internet connection and try again."
            )

        except (KeyError, ValueError, TypeError):
            error = (
                "The weather service returned unexpected data. "
                "Please try again later."
            )

    return render_template(
        "index.html",
        city=city,
        weather=weather,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
