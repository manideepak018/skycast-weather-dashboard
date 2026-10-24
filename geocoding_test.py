
import requests

url = "https://geocoding-api.open-meteo.com/v1/search"

city = input("Enter city name: ")

params = {
    "name": city,
    "count": 1,
    "language": "en"
}

response = requests.get(url, params=params, timeout=15)
response.raise_for_status()

data = response.json()

print(data)
