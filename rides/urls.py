
from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_ride, name="create_ride"),
    path("list/", views.ride_list, name="ride_list"),
    path("<int:ride_id>/data/", views.ride_detail_data, name="ride_detail_data"),
    path("<int:ride_id>/", views.ride_detail, name="ride_detail"),
    path("<int:ride_id>/update/", views.update_ride, name="update_ride"),
    path("<int:ride_id>/cancel/", views.cancel_ride, name="cancel_ride"),
    path("fare-preview/", views.fare_preview, name="fare_preview"),
]