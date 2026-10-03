from django.test import SimpleTestCase

from routing.services.optimizer import optimize_fuel_stops


class FuelOptimizerTests(SimpleTestCase):

    def test_route_under_500_miles_needs_no_purchase(self):

        result = optimize_fuel_stops(
            route_distance_miles=400,
            stations=[],
        )

        self.assertEqual(
            result["total_fuel_gallons"],
            40.0,
        )

        self.assertEqual(
            result["total_fuel_purchased"],
            0.0,
        )

        self.assertEqual(
            result["total_fuel_cost"],
            0.0,
        )

        self.assertEqual(
            result["fuel_stops"],
            [],
        )

    def test_cheaper_reachable_station_is_selected(self):

        stations = [
            {
                "name": "Station A",
                "price": 3.50,
                "route_position": 200,
            },
            {
                "name": "Station B",
                "price": 3.00,
                "route_position": 400,
            },
            {
                "name": "Station C",
                "price": 2.80,
                "route_position": 600,
            },
            {
                "name": "Station D",
                "price": 3.20,
                "route_position": 800,
            },
        ]

        result = optimize_fuel_stops(
            route_distance_miles=950,
            stations=stations,
        )

        self.assertEqual(
            result["total_fuel_gallons"],
            95.0,
        )

        self.assertEqual(
            result["total_fuel_purchased"],
            45.0,
        )

        self.assertEqual(
            result["total_fuel_cost"],
            128.0,
        )

        self.assertEqual(
            len(result["fuel_stops"]),
            2,
        )

        self.assertEqual(
            result["fuel_stops"][0]["station_name"],
            "Station B",
        )

        self.assertEqual(
            result["fuel_stops"][1]["station_name"],
            "Station C",
        )

    def test_no_reachable_station_raises_error(self):

        stations = [
            {
                "name": "Station A",
                "price": 3.00,
                "route_position": 600,
            }
        ]

        with self.assertRaises(ValueError):

            optimize_fuel_stops(
                route_distance_miles=1000,
                stations=stations,
            )