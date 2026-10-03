
import requests
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RouteRequestSerializer
from .services.fuel import find_stations_near_route
from .services.geocoding import geocode_city
from .services.geo import build_route_distances
from .services.optimizer import optimize_fuel_stops
from .services.routing import get_route


class RouteAPIView(APIView):

    def post(self, request):

        # ---------------------------------------------------------
        # VALIDATE REQUEST
        # ---------------------------------------------------------

        serializer = RouteRequestSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = serializer.validated_data["start"]
        finish = serializer.validated_data["finish"]

        # ---------------------------------------------------------
        # PARSE START / FINISH
        # ---------------------------------------------------------

        try:

            start_city, start_state = start.rsplit(
                ",",
                1,
            )

            finish_city, finish_state = finish.rsplit(
                ",",
                1,
            )

            start_city = start_city.strip()
            start_state = start_state.strip()

            finish_city = finish_city.strip()
            finish_state = finish_state.strip()

        except ValueError:

            return Response(
                {
                    "error": (
                        "Locations must be provided as "
                        "'City, STATE'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # GEOCODE START / FINISH
        # ---------------------------------------------------------

        try:

            start_location = geocode_city(
                start_city,
                start_state,
            )

            finish_location = geocode_city(
                finish_city,
                finish_state,
            )

        except requests.RequestException:

            return Response(
                {
                    "error": (
                        "Geocoding service is temporarily "
                        "unavailable."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except ValueError as exc:

            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # GET ROUTE
        # ---------------------------------------------------------

        try:

            route = get_route(
                start_lat=start_location["latitude"],
                start_lon=start_location["longitude"],
                finish_lat=finish_location["latitude"],
                finish_lon=finish_location["longitude"],
            )

        except requests.RequestException:

            return Response(
                {
                    "error": (
                        "Routing service is temporarily "
                        "unavailable."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except ValueError as exc:

            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # BUILD ROUTE DISTANCES
        # ---------------------------------------------------------

        route_points = build_route_distances(
            route["geometry"]["coordinates"]
        )

        # ---------------------------------------------------------
        # FIND FUEL STATIONS
        # ---------------------------------------------------------

        stations = find_stations_near_route(
            route_points
        )

        # ---------------------------------------------------------
        # OPTIMIZE FUEL
        # ---------------------------------------------------------

        try:

            fuel_plan = optimize_fuel_stops(
                route_distance_miles=route[
                    "distance_miles"
                ],
                stations=stations,
            )

        except ValueError as exc:

            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # RESPONSE
        # ---------------------------------------------------------

        return Response(
            {
                "start": {
                    "city": start_city,
                    "state": start_state,
                    "latitude": start_location[
                        "latitude"
                    ],
                    "longitude": start_location[
                        "longitude"
                    ],
                },
                "finish": {
                    "city": finish_city,
                    "state": finish_state,
                    "latitude": finish_location[
                        "latitude"
                    ],
                    "longitude": finish_location[
                        "longitude"
                    ],
                },
                "route": {
                    "distance_miles": round(
                        route["distance_miles"],
                        2,
                    ),
                    "duration_hours": round(
                        route["duration_hours"],
                        2,
                    ),
                    "geometry": route[
                        "geometry"
                    ],
                },
                "fuel": {
                    "vehicle_range_miles": 500,
                    "fuel_efficiency_mpg": 10,
                    "tank_capacity_gallons": 50,
                    "total_fuel_gallons": (
                        fuel_plan[
                            "total_fuel_gallons"
                        ]
                    ),
                    "total_fuel_purchased": (
                        fuel_plan[
                            "total_fuel_purchased"
                        ]
                    ),
                    "total_fuel_cost": (
                        fuel_plan[
                            "total_fuel_cost"
                        ]
                    ),
                    "fuel_stops": fuel_plan[
                        "fuel_stops"
                    ],
                },
            },
            status=status.HTTP_200_OK,
        )

def map_view(request):
    return render(request, "routing/map.html")