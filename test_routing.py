import requests


url = "https://router.project-osrm.org/route/v1/driving/-86.80249,33.52066;-85.25049,31.57184"

params = {
    "overview": "full",
    "geometries": "geojson",
    "steps": "false",
}

response = requests.get(
    url,
    params=params,
    timeout=30,
)

response.raise_for_status()

data = response.json()

print("Status:", data["code"])

route = data["routes"][0]

print("Distance:", route["distance"] / 1609.344, "miles")

print("Duration:", route["duration"] / 3600, "hours")

print("Geometry points:", len(route["geometry"]["coordinates"]))