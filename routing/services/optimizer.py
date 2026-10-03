FUEL_EFFICIENCY_MPG = 10.0
MAX_RANGE_MILES = 500.0
TANK_CAPACITY_GALLONS = 50.0


def optimize_fuel_stops(route_distance_miles: float, stations: list):

    # If the destination is reachable with the starting full tank,
    # no fuel purchase is necessary.
    if route_distance_miles <= MAX_RANGE_MILES:
        return {
            "fuel_stops": [],
            "total_fuel_gallons": round(
                route_distance_miles / FUEL_EFFICIENCY_MPG,
                4,
            ),
            "total_fuel_purchased": 0.0,
            "total_fuel_cost": 0.0,
        }

    # Only stations located between the start and destination.
    stations = sorted(
        [
            station
            for station in stations
            if 0 < station["route_position"] < route_distance_miles
        ],
        key=lambda station: station["route_position"],
    )

    if not stations:
        raise ValueError(
            "No fuel stations are available on the route."
        )

    # If multiple stations map to approximately the same route position,
    # keep the cheapest one.
    unique_stations = {}

    for station in stations:

        position = round(
            station["route_position"],
            3,
        )

        if (
            position not in unique_stations
            or station["price"]
            < unique_stations[position]["price"]
        ):
            unique_stations[position] = station

    stations = sorted(
        unique_stations.values(),
        key=lambda station: station["route_position"],
    )

    fuel_remaining = TANK_CAPACITY_GALLONS
    current_position = 0.0

    current_station = None
    current_price = None

    fuel_stops = []

    # ---------------------------------------------------------
    # INITIAL STATION
    # ---------------------------------------------------------

    # We start with a full tank, so there is no reason to stop
    # at an expensive early station if a cheaper reachable station
    # is available within the initial 500-mile range.

    initially_reachable = [
        station
        for station in stations
        if station["route_position"] <= MAX_RANGE_MILES
    ]

    if not initially_reachable:

        raise ValueError(
            "No fuel station is reachable within the initial "
            "500-mile vehicle range."
        )

    # Choose the cheapest reachable station.
    first_station = min(
        initially_reachable,
        key=lambda station: station["price"],
    )

    distance_to_station = (
        first_station["route_position"]
        - current_position
    )

    fuel_remaining -= (
        distance_to_station / FUEL_EFFICIENCY_MPG
    )

    current_position = first_station["route_position"]
    current_station = first_station
    current_price = first_station["price"]

    # ---------------------------------------------------------
    # OPTIMIZATION LOOP
    # ---------------------------------------------------------

    while True:

        distance_to_destination = (
            route_distance_miles - current_position
        )

        # Destination is reachable with current fuel.
        if (
            distance_to_destination
            <= fuel_remaining * FUEL_EFFICIENCY_MPG
        ):
            break

        # Stations reachable from the current station.
        reachable = [
            station
            for station in stations
            if (
                station["route_position"] > current_position
                and
                station["route_position"]
                - current_position
                <= MAX_RANGE_MILES
            )
        ]

        if not reachable:

            raise ValueError(
                "No reachable fuel station is available "
                "within the vehicle's 500-mile range."
            )

        # -----------------------------------------------------
        # FIND NEXT CHEAPER STATION
        # -----------------------------------------------------

        cheaper_station = None

        for station in reachable:

            if station["price"] < current_price:

                cheaper_station = station
                break

        # -----------------------------------------------------
        # CASE 1:
        # A cheaper station is reachable.
        # Buy only enough fuel to reach it.
        # -----------------------------------------------------

        if cheaper_station is not None:

            target = cheaper_station

            distance_to_target = (
                target["route_position"]
                - current_position
            )

            required_fuel = (
                distance_to_target
                / FUEL_EFFICIENCY_MPG
            )

            fuel_to_purchase = max(
                0.0,
                required_fuel - fuel_remaining,
            )

        # -----------------------------------------------------
        # CASE 2:
        # No cheaper station is reachable.
        #
        # If destination is within 500 miles, buy only enough
        # to reach the destination.
        #
        # Otherwise fill the tank and travel to the farthest
        # reachable station.
        # -----------------------------------------------------

        else:

            if (
                distance_to_destination
                <= MAX_RANGE_MILES
            ):

                target = None

                required_fuel = (
                    distance_to_destination
                    / FUEL_EFFICIENCY_MPG
                )

                fuel_to_purchase = max(
                    0.0,
                    required_fuel - fuel_remaining,
                )

            else:

                target = reachable[-1]

                fuel_to_purchase = (
                    TANK_CAPACITY_GALLONS
                    - fuel_remaining
                )

        # Safety limits.
        fuel_to_purchase = min(
            fuel_to_purchase,
            TANK_CAPACITY_GALLONS - fuel_remaining,
        )

        fuel_to_purchase = max(
            0.0,
            fuel_to_purchase,
        )

        # -----------------------------------------------------
        # PURCHASE FUEL
        # -----------------------------------------------------

        if fuel_to_purchase > 0:

            fuel_cost = (
                fuel_to_purchase
                * current_price
            )

            fuel_stops.append(
                {
                    "station_name": current_station["name"],
                    "address": current_station.get(
                        "address",
                        "",
                    ),
                    "city": current_station.get(
                        "city",
                        "",
                    ),
                    "state": current_station.get(
                        "state",
                        "",
                    ),
                    "latitude": current_station.get(
                        "latitude"
                    ),
                    "longitude": current_station.get(
                        "longitude"
                    ),
                    "route_position": round(
                        current_position,
                        2,
                    ),
                    "fuel_purchased_gallons": round(
                        fuel_to_purchase,
                        4,
                    ),
                    "fuel_price_per_gallon": round(
                        current_price,
                        3,
                    ),
                    "fuel_cost": round(
                        fuel_cost,
                        2,
                    ),
                    "fuel_remaining_before_purchase": round(
                        fuel_remaining,
                        4,
                    ),
                }
            )

            fuel_remaining += fuel_to_purchase

        # -----------------------------------------------------
        # DESTINATION
        # -----------------------------------------------------

        if target is None:

            fuel_remaining -= (
                distance_to_destination
                / FUEL_EFFICIENCY_MPG
            )

            current_position = route_distance_miles

            break

        # -----------------------------------------------------
        # TRAVEL TO NEXT STATION
        # -----------------------------------------------------

        distance_to_target = (
            target["route_position"]
            - current_position
        )

        fuel_remaining -= (
            distance_to_target
            / FUEL_EFFICIENCY_MPG
        )

        if fuel_remaining < -0.0001:

            raise ValueError(
                "Fuel calculation produced an invalid "
                "negative fuel balance."
            )

        fuel_remaining = max(
            0.0,
            fuel_remaining,
        )

        current_position = target[
            "route_position"
        ]

        current_station = target
        current_price = target["price"]

    # ---------------------------------------------------------
    # FINAL TOTALS
    # ---------------------------------------------------------

    total_fuel_gallons = (
        route_distance_miles
        / FUEL_EFFICIENCY_MPG
    )

    total_fuel_purchased = sum(
        stop["fuel_purchased_gallons"]
        for stop in fuel_stops
    )

    total_fuel_cost = sum(
        stop["fuel_cost"]
        for stop in fuel_stops
    )

    return {
        "fuel_stops": fuel_stops,
        "total_fuel_gallons": round(
            total_fuel_gallons,
            4,
        ),
        "total_fuel_purchased": round(
            total_fuel_purchased,
            4,
        ),
        "total_fuel_cost": round(
            total_fuel_cost,
            2,
        ),
    }