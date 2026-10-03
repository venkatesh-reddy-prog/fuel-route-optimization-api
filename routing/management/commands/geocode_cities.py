import time

import requests
from django.core.management.base import BaseCommand

from routing.models import CityLocation, FuelStation


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


class Command(BaseCommand):
    help = "Geocode unique US fuel-station cities using Open-Meteo"

    def handle(self, *args, **options):

        locations = (
            FuelStation.objects
            .values("city", "state")
            .distinct()
            .order_by("state", "city")
        )

        total = len(locations)

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {total} unique city/state combinations."
            )
        )

        created = 0
        skipped = 0
        failed = 0
        non_us = 0

        session = requests.Session()

        for index, location in enumerate(locations, start=1):

            city = location["city"].strip()
            state = location["state"].strip().upper()

            # Skip Canadian / non-US locations
            if state not in US_STATES:
                non_us += 1
                continue

            state_name = US_STATES[state]

            # Already geocoded
            if CityLocation.objects.filter(
                city__iexact=city,
                state__iexact=state,
            ).exists():
                skipped += 1
                continue

            params = {
                "name": city,
                "count": 10,
                "countryCode": "US",
                "language": "en",
                "format": "json",
            }

            try:

                response = session.get(
                    GEOCODING_URL,
                    params=params,
                    timeout=15,
                )

                response.raise_for_status()

                data = response.json()
                results = data.get("results", [])

                match = None

                for result in results:

                    if result.get("country_code") != "US":
                        continue

                    admin1 = result.get("admin1", "").strip()

                    if admin1.lower() == state_name.lower():
                        match = result
                        break

                if match is None:

                    failed += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"[{index}/{total}] "
                            f"No match: {city}, {state}"
                        )
                    )

                    continue

                CityLocation.objects.create(
                    city=city,
                    state=state,
                    latitude=match["latitude"],
                    longitude=match["longitude"],
                )

                created += 1

                self.stdout.write(
                    f"[{index}/{total}] "
                    f"{city}, {state} -> "
                    f"{match['latitude']}, "
                    f"{match['longitude']}"
                )

                # Conservative request rate
                time.sleep(1)

            except requests.RequestException as exc:

                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"[{index}/{total}] "
                        f"Request failed for "
                        f"{city}, {state}: {exc}"
                    )
                )

                # Give the service a little recovery time
                time.sleep(3)

        self.stdout.write(
            self.style.SUCCESS(
                "\nGeocoding complete.\n"
                f"Created: {created}\n"
                f"Skipped: {skipped}\n"
                f"Failed: {failed}\n"
                f"Non-US skipped: {non_us}"
            )
        )