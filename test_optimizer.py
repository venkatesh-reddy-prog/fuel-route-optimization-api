from routing.services.optimizer import optimize_fuel_stops


stations = [
    {
        "name": "Station A",
        "route_position": 200,
        "price": 3.50,
    },
    {
        "name": "Station B",
        "route_position": 400,
        "price": 3.00,
    },
    {
        "name": "Station C",
        "route_position": 600,
        "price": 2.80,
    },
    {
        "name": "Station D",
        "route_position": 800,
        "price": 3.20,
    },
]


result = optimize_fuel_stops(
    route_distance_miles=950,
    stations=stations,
)


print("\n===== OPTIMIZER TEST =====")

print(
    "Total fuel required:",
    result["total_fuel_gallons"],
    "gallons",
)

print(
    "Total fuel purchased:",
    result["total_fuel_purchased"],
    "gallons",
)

print(
    "Total fuel cost: $",
    result["total_fuel_cost"],
)


print("\nFuel stops:")

for stop in result["fuel_stops"]:
    print(
        f"{stop['station_name']} | "
        f"position={stop['route_position']} mi | "
        f"price=${stop['fuel_price_per_gallon']:.3f} | "
        f"purchased={stop['fuel_purchased_gallons']:.2f} gal | "
        f"cost=${stop['fuel_cost']:.2f}"
    )