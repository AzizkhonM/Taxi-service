from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rides.models import Ride
from .forms import CarForm
from .models import Car

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse


@login_required
def dashboard(request):
    if request.user.role != "driver":
        return render(request, "rides/access_denied.html")

    rides = Ride.objects.filter(
        status=Ride.Status.PENDING,
        driver__isnull=True
    ).order_by("-created_at")

    my_rides = Ride.objects.filter(
        driver=request.user.driver_profile,
        status__in=[
            Ride.Status.ACCEPTED,
            Ride.Status.ARRIVED,
            Ride.Status.IN_PROGRESS,
            Ride.Status.COMPLETED,
        ]
    ).order_by("-created_at")

    return render(request, "drivers/dashboard.html", {
        "rides": rides,
        "my_rides": my_rides,
    })
    
    
@login_required
@require_GET
def dashboard_data(request):
    if request.user.role != "driver":
        return JsonResponse({"error": "Access denied"}, status=403)

    rides = Ride.objects.filter(
        status=Ride.Status.PENDING,
        driver__isnull=True
    ).order_by("-created_at")

    my_rides = Ride.objects.filter(
        driver=request.user.driver_profile,
        status__in=[
            Ride.Status.ACCEPTED,
            Ride.Status.ARRIVED,
            Ride.Status.IN_PROGRESS,
            Ride.Status.COMPLETED,
        ]
    ).order_by("-created_at")

    def serialize_ride(ride):
        return {
            "id": ride.id,
            "pickup": ride.pickup_address,
            "destination": ride.destination_address,
            "distance": str(ride.distance_km),
            "duration": str(ride.duration_minutes),
            "fare": ride.fare,
            "status": ride.status,
            "status_display": ride.get_status_display(),
        }

    return JsonResponse({
        "rides": [serialize_ride(ride) for ride in rides],
        "my_rides": [serialize_ride(ride) for ride in my_rides],
    })
    
@login_required
@require_POST
def accept_ride(request, ride_id):
    if request.user.role != "driver":
        return JsonResponse({"error": "Access denied"}, status=403)

    updated = Ride.objects.filter(
        id=ride_id,
        status=Ride.Status.PENDING,
        driver__isnull=True
    ).update(
        driver=request.user.driver_profile,
        status=Ride.Status.ACCEPTED
    )

    if not updated:
        return JsonResponse({
            "error": "This ride is no longer available."
        }, status=409)

    return JsonResponse({"success": True})

@login_required
@require_POST
def update_ride_status(request, ride_id):
    if request.user.role != "driver":
        return JsonResponse({"error": "Access denied"}, status=403)

    ride = get_object_or_404(
        Ride,
        id=ride_id,
        driver=request.user.driver_profile
    )

    next_status = {
        Ride.Status.ACCEPTED: Ride.Status.ARRIVED,
        Ride.Status.ARRIVED: Ride.Status.IN_PROGRESS,
        Ride.Status.IN_PROGRESS: Ride.Status.COMPLETED,
    }

    if ride.status not in next_status:
        return JsonResponse({"error": "Invalid status"}, status=400)

    ride.status = next_status[ride.status]
    ride.save()

    return JsonResponse({"success": True})

@login_required
def car_form(request):
    if request.user.role != "driver":
        return render(request, "rides/access_denied.html")

    driver = request.user.driver_profile
    car = Car.objects.filter(driver=driver).first()

    if request.method == "POST":
        form = CarForm(request.POST, instance=car)

        if form.is_valid():
            car = form.save(commit=False)
            car.driver = driver
            car.save()

            return redirect("driver_dashboard")
    else:
        form = CarForm(instance=car)

    return render(request, "drivers/car_form.html", {
        "form": form,
        "car": car,
    })