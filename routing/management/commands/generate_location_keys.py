from django.core.management.base import BaseCommand

from routing.models import FuelStation


class Command(BaseCommand):
    help = "Generate normalized location keys for fuel stations"

    def handle(self, *args, **options):
        stations = FuelStation.objects.all()

        updated = 0

        for station in stations:
            parts = [
                station.address,
                station.city,
                station.state,
                "USA",
            ]

            location_key = " | ".join(
                part.strip().lower()
                for part in parts
                if part and part.strip()
            )

            if station.location_key != location_key:
                station.location_key = location_key
                station.save(
                    update_fields=[
                        "location_key",
                        "updated_at",
                    ]
                )
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated location keys for {updated} stations."
            )
        )