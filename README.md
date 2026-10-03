# Fuel Route Optimization API

A Django REST API that calculates a driving route between two US locations and determines cost-effective fuel stops using the provided fuel-price dataset.

The application combines:

- Django REST Framework
- OSRM for driving routes
- Open-Meteo Geocoding API for city coordinates
- Leaflet + OpenStreetMap for map visualization
- The supplied fuel-price dataset
- A fuel-cost optimization algorithm

---

## Features

- Calculate a driving route between two US cities
- Return route distance and estimated travel duration
- Return route geometry as GeoJSON
- Identify fuel stations near the calculated route
- Select cost-effective fuel stops based on fuel prices
- Support multiple fuel stops
- Respect the vehicle's maximum range
- Calculate total fuel consumption
- Calculate total fuel purchased
- Calculate total fuel cost
- Display the route and fuel stops on an interactive map
- Automated tests for fuel optimization logic

---

## Vehicle Assumptions

The assessment specifies the following vehicle constraints:

| Parameter | Value |
|---|---:|
| Maximum range | 500 miles |
| Fuel efficiency | 10 MPG |
| Tank capacity | 50 gallons |

Fuel consumption is calculated as:

```text
Fuel Required = Route Distance / 10 MPG
```

---

## Architecture

```text
                         Client
                           |
                           v
                  Django REST API
                           |
             +-------------+-------------+
             |                           |
             v                           v
        Open-Meteo                      OSRM
        Geocoding                     Routing
             |                           |
             +-------------+-------------+
                           |
                           v
                    Route Geometry
                           |
                           v
                   Station Filtering
                           |
                           v
                    Fuel Optimizer
                           |
                           v
                    Optimized Stops
                           |
                           v
                     JSON Response
                           |
                           v
                  Leaflet Web Map
```

The web map consumes the same API response and renders the route geometry and selected fuel stops.

---

## Project Structure

```text
fuel-route-api/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── data/
│   └── fuel-prices-for-be-assessment.xlsx
│
├── routing/
│   ├── management/
│   │   └── commands/
│   │       ├── generate_location_keys.py
│   │       ├── geocode_cities.py
│   │       └── import_fuel_prices.py
│   │
│   ├── migrations/
│   │
│   ├── services/
│   │   ├── fuel.py
│   │   ├── geo.py
│   │   ├── geocoding.py
│   │   ├── optimizer.py
│   │   └── routing.py
│   │
│   ├── models.py
│   ├── serializers.py
│   ├── test_optimizer.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
├── README.md
│
└── test_*.py
```

---

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd fuel-route-api
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run migrations

```powershell
python manage.py migrate
```

### 5. Import fuel prices

The assessment dataset is located at:

```text
data/fuel-prices-for-be-assessment.xlsx
```

Run:

```powershell
python manage.py import_fuel_prices
```

The importer reads the supplied Excel file and creates the fuel-price records.

### 6. Generate normalized station location keys

```powershell
python manage.py generate_location_keys
```

### 7. Populate city coordinates

The application uses the Open-Meteo Geocoding API to populate city coordinates used for fuel-station positioning.

```powershell
python manage.py geocode_cities
```

### 8. Start the development server

```powershell
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

## API

### Calculate Route

**Endpoint**

```text
POST /api/v1/route/
```

**Full URL**

```text
http://127.0.0.1:8000/api/v1/route/
```

### Request

```json
{
    "start": "Birmingham, AL",
    "finish": "Dallas, TX"
}
```

### Example Response

```json
{
    "start": {
        "city": "Birmingham",
        "state": "AL",
        "latitude": 33.52066,
        "longitude": -86.80249
    },
    "finish": {
        "city": "Dallas",
        "state": "TX",
        "latitude": 32.78306,
        "longitude": -96.80667
    },
    "route": {
        "distance_miles": 638.7,
        "duration_hours": 11.54,
        "geometry": {
            "type": "LineString",
            "coordinates": []
        }
    },
    "fuel": {
        "vehicle_range_miles": 500,
        "fuel_efficiency_mpg": 10,
        "tank_capacity_gallons": 50,
        "total_fuel_gallons": 63.8695,
        "total_fuel_purchased": 13.8695,
        "total_fuel_cost": 38.77,
        "fuel_stops": []
    }
}
```

The actual API response contains the complete GeoJSON route geometry and selected fuel stops.

---

## Fuel Optimization

The optimizer models the vehicle as starting with a full 50-gallon tank.

For routes longer than the vehicle's 500-mile range, the algorithm evaluates fuel stations positioned along the route.

The strategy is:

1. Start with a full tank.
2. Identify reachable fuel stations.
3. Prefer a cheaper reachable station when one exists.
4. Purchase only the amount required to reach that cheaper station.
5. If no cheaper reachable station exists, purchase enough fuel to continue toward the next useful station or destination.
6. Never exceed the 50-gallon tank capacity.
7. Ensure every travel segment remains within the 500-mile vehicle range.
8. Calculate total fuel consumption and purchase cost.

Implementation:

```text
routing/services/optimizer.py
```

---

## Station Search

Fuel stations are filtered using a geographic corridor around the calculated route.

Current corridor:

```text
25 miles
```

A geographic bounding-box filter is applied first to reduce unnecessary distance calculations.

Stations that pass the bounding-box filter are then checked using the Haversine distance calculation.

Implementation:

```text
routing/services/fuel.py
```

---

## Routing

Driving routes are obtained from the public OSRM routing service.

The API requests:

- Driving route
- Full route geometry
- GeoJSON geometry

The resulting route geometry is returned by the API and used to determine the position of fuel stations along the route.

Implementation:

```text
routing/services/routing.py
```

---

## Geocoding

Start and destination cities are converted into coordinates using the Open-Meteo Geocoding API.

Example:

```text
Birmingham, AL
       |
       v
33.52066, -86.80249
```

Implementation:

```text
routing/services/geocoding.py
```

---

## Interactive Map

The project includes an interactive Leaflet map:

```text
http://127.0.0.1:8000/api/v1/map/
```

The map displays:

- Start location
- Destination
- Driving route
- Fuel stops
- Fuel price
- Fuel purchased
- Fuel cost
- Route distance
- Total fuel cost

The map uses Leaflet for visualization and OpenStreetMap tiles.

---

## Example Result

For:

```text
Birmingham, AL
       |
       v
Dallas, TX
```

The current implementation produces approximately:

```text
Route distance:        638.7 miles
Fuel required:          63.8695 gallons
Fuel purchased:         13.8695 gallons
Fuel cost:              $38.77
Fuel stops:              4
```

---

## Testing

Run the automated tests with:

```powershell
python manage.py test routing
```

Current tests cover:

### Short route

A route below the 500-mile vehicle range should not require a fuel purchase.

### Cheaper reachable station

The optimizer should prefer a cheaper reachable station when appropriate.

### Unreachable route

The optimizer should raise an error when no fuel station is reachable within the vehicle's maximum range.

Current result:

```text
Found 3 test(s).

Ran 3 tests

OK
```

---

## Error Handling

The API handles:

- Invalid request payloads
- Invalid location format
- Geocoding failures
- Routing failures
- Missing fuel stations
- Unreachable fuel segments
- External service failures

External-service failures return appropriate HTTP error responses instead of exposing raw exceptions.

---

## External Services

### OSRM

Used for driving-route calculation.

```text
https://router.project-osrm.org/
```

### Open-Meteo

Used for city geocoding.

```text
https://geocoding-api.open-meteo.com/
```

### OpenStreetMap

Used as the map tile provider for the interactive map.

### Leaflet

Used for client-side map rendering.

---

## Assumptions

- Input locations are US cities in the format `City, STATE`.
- Fuel prices in the supplied dataset are treated as price per gallon.
- The vehicle starts with a full tank.
- Fuel efficiency is fixed at 10 MPG.
- Maximum vehicle range is 500 miles.
- Tank capacity is 50 gallons.
- Fuel stations are considered candidates when they are within the configured route corridor.
- Route distance is based on the selected routing provider.
- Fuel cost is based on the supplied fuel-price dataset.
- External routing and geocoding services are required for live requests.

---

## Development Checks

Run Django system checks:

```powershell
python manage.py check
```

Run tests:

```powershell
python manage.py test routing
```

Run the application:

```powershell
python manage.py runserver
```

---

## Postman

Example request:

```text
POST http://127.0.0.1:8000/api/v1/route/
```

Headers:

```text
Content-Type: application/json
```

Body:

```json
{
    "start": "Birmingham, AL",
    "finish": "Dallas, TX"
}
```

---

## License

This project was developed as part of a backend engineering assessment.