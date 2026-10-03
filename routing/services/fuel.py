from routing.models import CityLocation, FuelStation

from .geo import haversine_miles


MAX_DISTANCE_FROM_ROUTE_MILES = 25.0


def get_station_locations():
    """
    Load cached city coordinates.

    Key:
        (city, state)

    Value:
        latitude / longitude
    """

    return {
        (
            location.city.strip().lower(),
            location.state.strip().upper(),
        ): {
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
        for location in CityLocation.objects.all()
    }


def get_route_bounds(route_points):
    """
    Build a geographic bounding box around the route.

    The 25-mile corridor is approximated in degrees.
    """

    latitudes = [
        point["latitude"]
        for point in route_points
    ]

    longitudes = [
        point["longitude"]
        for point in route_points
    ]

    padding_lat = (
        MAX_DISTANCE_FROM_ROUTE_MILES / 69.0
    )

    average_latitude = sum(latitudes) / len(latitudes)

    longitude_miles_per_degree = (
        69.0
        * max(
            0.1,
            abs(__import__("math").cos(
                __import__("math").radians(
                    average_latitude
                )
            )),
        )
    )

    padding_lon = (
        MAX_DISTANCE_FROM_ROUTE_MILES
        / longitude_miles_per_degree
    )

    return {
        "min_lat": min(latitudes) - padding_lat,
        "max_lat": max(latitudes) + padding_lat,
        "min_lon": min(longitudes) - padding_lon,
        "max_lon": max(longitudes) + padding_lon,
    }


def distance_from_route(
    station_lat,
    station_lon,
    route_points,
):
    """
    Calculate the closest point on the route
    using Haversine distance.
    """

    closest_distance = float("inf")
    closest_route_position = None

    for point in route_points:

        distance = haversine_miles(
            station_lat,
            station_lon,
            point["latitude"],
            point["longitude"],
        )

        if distance < closest_distance:

            closest_distance = distance

            closest_route_position = (
                point["distance_miles"]
            )

    return {
        "distance_from_route": closest_distance,
        "route_position": closest_route_position,
    }


def find_stations_near_route(route_points):
    """
    Find fuel stations within the configured
    distance corridor around the route.

    Uses a bounding-box pre-filter before performing
    expensive Haversine calculations.
    """

    if not route_points:
        return []

    locations = get_station_locations()

    bounds = get_route_bounds(route_points)

    candidates = []

    stations = FuelStation.objects.all()

    for station in stations:

        key = (
            station.city.strip().lower(),
            station.state.strip().upper(),
        )

        coordinates = locations.get(key)

        if coordinates is None:
            continue

        latitude = coordinates["latitude"]
        longitude = coordinates["longitude"]

        # -----------------------------------------------------
        # FAST BOUNDING-BOX FILTER
        # -----------------------------------------------------

        if latitude < bounds["min_lat"]:
            continue

        if latitude > bounds["max_lat"]:
            continue

        if longitude < bounds["min_lon"]:
            continue

        if longitude > bounds["max_lon"]:
            continue

        # -----------------------------------------------------
        # EXACT ROUTE DISTANCE
        # -----------------------------------------------------

        result = distance_from_route(
            latitude,
            longitude,
            route_points,
        )

        if (
            result["distance_from_route"]
            > MAX_DISTANCE_FROM_ROUTE_MILES
        ):
            continue

        candidates.append(
            {
                "station_id": station.id,
                "truckstop_id": station.truckstop_id,
                "name": station.name,
                "address": station.address,
                "city": station.city,
                "state": station.state,
                "price": float(station.price),
                "latitude": latitude,
                "longitude": longitude,
                "distance_from_route": round(
                    result["distance_from_route"],
                    2,
                ),
                "route_position": result[
                    "route_position"
                ],
            }
        )

    candidates.sort(
        key=lambda station: station["route_position"]
    )

    return candidates