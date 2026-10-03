import requests


OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_route(
    start_lat: float,
    start_lon: float,
    finish_lat: float,
    finish_lon: float,
) -> dict:

    coordinates = (
        f"{start_lon},{start_lat};"
        f"{finish_lon},{finish_lat}"
    )

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
    }

    response = requests.get(
        f"{OSRM_URL}/{coordinates}",
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("Routing service could not find a route.")

    route = data["routes"][0]

    return {
        "distance_miles": route["distance"] / 1609.344,
        "duration_hours": route["duration"] / 3600,
        "geometry": route["geometry"],
    }