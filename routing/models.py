from django.db import models


class FuelStation(models.Model):
    truckstop_id = models.BigIntegerField()

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    rack_id = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=3)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    geocoded = models.BooleanField(default=False)

    location_key = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"


class CityLocation(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)

    latitude = models.FloatField()
    longitude = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["city", "state"],
                name="unique_city_state",
            )
        ]

    def __str__(self):
        return f"{self.city}, {self.state}"