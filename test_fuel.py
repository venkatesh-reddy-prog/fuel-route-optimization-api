import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()


from routing.services.geo import build_route_distances
from routing.services.routing import get_route
from routing.services.fuel import find_stations_near_route


start_lat = 33.52066
start_lon = -86.80249

finish_lat = 31.57184
finish_lon = -85.25049


route = get_route(
    start_lat=start_lat,
    start_lon=start_lon,
    finish_lat=finish_lat,
    finish_lon=finish_lon,
)


coordinates = route["geometry"]["coordinates"]

route_points = build_route_distances(coordinates)


print("Route distance:")
print(route["distance_miles"])


print("\nSearching for nearby fuel stations...")


stations = find_stations_near_route(route_points)


print("\nStations found:", len(stations))


for station in stations[:20]:

    print(
        station["name"],
        "|",
        station["city"],
        station["state"],
        "| Price:",
        station["price"],
        "| Route position:",
        round(station["route_position"], 2),
        "miles",
        "| Distance from route:",
        round(station["distance_from_route"], 2),
        "miles",
    )