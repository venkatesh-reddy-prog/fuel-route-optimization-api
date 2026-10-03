from pathlib import Path

import pandas as pd

from django.core.management.base import BaseCommand

from routing.models import FuelStation


class Command(BaseCommand):
    help = "Import fuel station prices from the assessment Excel file"

    def handle(self, *args, **options):
        file_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "fuel-prices-for-be-assessment.xlsx"
        )

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Excel file not found: {file_path}"
                )
            )
            return

        self.stdout.write(
            f"Reading fuel prices from: {file_path}"
        )

        df = pd.read_excel(file_path)

        self.stdout.write(
            f"Found {len(df)} records."
        )

        self.stdout.write(
            f"Columns: {list(df.columns)}"
        )

        stations = []

        for _, row in df.iterrows():
            station = FuelStation(
                truckstop_id=int(row["OPIS Truckstop ID"]),
                name=str(row["Truckstop Name"]),
                address=(
                    str(row["Address"])
                    if pd.notna(row["Address"])
                    else ""
                ),
                city=str(row["City"]),
                state=str(row["State"]),
                rack_id=(
                    str(row["Rack ID"])
                    if pd.notna(row["Rack ID"])
                    else ""
                ),
                price=float(row["Retail Price"]),
            )

            stations.append(station)

        FuelStation.objects.bulk_create(
            stations,
            batch_size=1000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created {len(stations)} fuel-price records."
            )
        )