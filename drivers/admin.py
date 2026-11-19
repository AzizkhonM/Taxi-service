from django.contrib import admin
from .models import Driver, Car, DriverLocation


admin.site.register(Driver)
admin.site.register(Car)
admin.site.register(DriverLocation)