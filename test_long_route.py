import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from routing.services.geo import build_route_distances
from routing.services.routing import get_route
from routing.services.fuel import find_stations_near_route
from routing.services.optimizer import optimize_fuel_stops


START_LAT = 33.52066
START_LON = -86.80249

FINISH_LAT = 32.7767
FINISH_LON = -96.7970


# 1. Get route
route = get_route(
    START_LAT,
    START_LON,
    FINISH_LAT,
    FINISH_LON,
)

print(f"Route distance: {route['distance_miles']:.1f} miles")


# 2. Build route points
route_points = build_route_distances(
    route["geometry"]["coordinates"]
)


# 3. Find fuel stations
stations = find_stations_near_route(
    route_points
)

print(f"Stations found: {len(stations)}")


# 4. Optimize fuel
fuel_plan = optimize_fuel_stops(
    route_distance_miles=route["distance_miles"],
    stations=stations,
)


# 5. Display result
print("\n===== FUEL PLAN =====")

print(
    f"Total fuel required: "
    f"{fuel_plan['total_fuel_gallons']:.2f} gallons"
)

print(
    f"Total fuel purchased: "
    f"{fuel_plan['total_fuel_purchased']:.2f} gallons"
)

print(
    f"Total fuel cost: "
    f"${fuel_plan['total_fuel_cost']:.2f}"
)


print("\n===== FUEL STOPS =====")

for stop in fuel_plan["fuel_stops"]:
    print(
        f"Position: {stop['route_position']:.1f} mi | "
        f"Price: ${stop['fuel_price_per_gallon']:.3f} | "
        f"Purchased: {stop['fuel_purchased_gallons']:.2f} gal | "
        f"Cost: ${stop['fuel_cost']:.2f}"
    )