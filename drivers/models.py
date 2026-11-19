from django.conf import settings
from django.db import models


class Driver(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile"
    )
    photo = models.ImageField(upload_to="drivers/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()


class Car(models.Model):
    driver = models.OneToOneField(
        Driver,
        on_delete=models.CASCADE,
        related_name="car"
    )
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    plate_number = models.CharField(max_length=20, unique=True)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"
    
    
    
class DriverLocation(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="locations"
    )

    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver} - {self.latitude}, {self.longitude}"