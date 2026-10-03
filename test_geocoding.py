import requests


url = "https://geocoding-api.open-meteo.com/v1/search"

params = {
    "name": "Harrold, TX",
    "count": 1,
    "countryCode": "US",
    "language": "en",
    "format": "json",
}

response = requests.get(
    url,
    params=params,
    timeout=15,
)

response.raise_for_status()

data = response.json()

print(data)