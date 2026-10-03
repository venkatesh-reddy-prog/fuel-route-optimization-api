import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()
from routing.services.geocoding import geocode_city
from routing.services.routing import get_route
from routing.services.geo import build_route_distances
from routing.services.fuel import find_stations_near_route
from routing.services.optimizer import optimize_fuel_stops


start = geocode_city("Birmingham", "AL")
finish = geocode_city("Dallas", "TX")

route = get_route(
    start_lat=start["latitude"],
    start_lon=start["longitude"],
    finish_lat=finish["latitude"],
    finish_lon=finish["longitude"],
)

route_points = build_route_distances(
    route["geometry"]["coordinates"]
)

stations = find_stations_near_route(
    route_points
)

fuel_plan = optimize_fuel_stops(
    route_distance_miles=route["distance_miles"],
    stations=stations,
)


print()
print("===== REAL ROUTE TEST =====")
print(
    "Route distance:",
    round(route["distance_miles"], 2),
    "miles",
)

print(
    "Stations found:",
    len(stations)
)

print()
print("===== FUEL PLAN =====")

print(
    "Total fuel required:",
    fuel_plan["total_fuel_gallons"],
    "gallons",
)

print(
    "Total fuel purchased:",
    fuel_plan["total_fuel_purchased"],
    "gallons",
)

print(
    "Total fuel cost: $",
    fuel_plan["total_fuel_cost"]
)

print()
print("===== FUEL STOPS =====")

for stop in fuel_plan["fuel_stops"]:

    print(
        f"{stop['station_name']} | "
        f"{stop['city']}, {stop['state']} | "
        f"position={stop['route_position']} mi | "
        f"price=${stop['fuel_price_per_gallon']:.3f} | "
        f"purchased={stop['fuel_purchased_gallons']:.2f} gal | "
        f"cost=${stop['fuel_cost']:.2f}"
    )