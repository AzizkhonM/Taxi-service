from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="driver_dashboard"),
    path("data/", views.dashboard_data, name="dashboard_data"),
    path("accept/<int:ride_id>/", views.accept_ride, name="accept_ride"),
    path("update-status/<int:ride_id>/", views.update_ride_status, name="update_ride_status"),
    path("car/", views.car_form, name="car_form"),
]