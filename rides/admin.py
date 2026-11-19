from django.contrib import admin
from .models import Customer, Ride


admin.site.register(Customer)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "driver",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("pickup_address", "destination_address")