from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_MILES = 3958.7613


def haversine_miles(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate great-circle distance between two coordinates.
    """

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_MILES * asin(sqrt(a))


def build_route_distances(coordinates: list) -> list:
    """
    Calculate cumulative distance along the route.

    Returns a list where each item contains:
    {
        "longitude": ...,
        "latitude": ...,
        "distance_miles": ...
    }
    """

    points = []

    cumulative_distance = 0.0

    for index, coordinate in enumerate(coordinates):

        longitude, latitude = coordinate

        if index > 0:

            previous_longitude, previous_latitude = coordinates[
                index - 1
            ]

            cumulative_distance += haversine_miles(
                previous_latitude,
                previous_longitude,
                latitude,
                longitude,
            )

        points.append(
            {
                "longitude": longitude,
                "latitude": latitude,
                "distance_miles": cumulative_distance,
            }
        )

    return points