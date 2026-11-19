
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from decimal import Decimal, InvalidOperation

from .forms import RideCreateForm
from .models import Ride
from .pricing import calculate_fare
from .routing import calculate_route_metrics


@login_required
def create_ride(request):
    if request.user.role != "customer":
        return render(request, "rides/access_denied.html")

    if request.method == "POST":
        form = RideCreateForm(request.POST)

        if form.is_valid():
            try:
                ride = form.save(commit=False)

                distance, duration = calculate_route_metrics(
                    ride.pickup_latitude,
                    ride.pickup_longitude,
                    ride.destination_latitude,
                    ride.destination_longitude,
                )

                ride.distance_km = distance
                ride.duration_minutes = duration

                ride.fare = calculate_fare(distance, duration)
                ride.customer = request.user.customer_profile

                ride.save()

                return redirect("profile")

            except ValueError as error:
                form.add_error(None, str(error))

    else:
        form = RideCreateForm()

    return render(
        request,
        "rides/create_ride.html",
        {"form": form, "mapbox_token": settings.MAPBOX_ACCESS_TOKEN},
    )

@login_required
def ride_list(request):
    if request.user.role != "customer":
        return render(request, "rides/access_denied.html")

    rides = Ride.objects.filter(
        customer=request.user.customer_profile
    ).order_by("-created_at")

    return render(request, "rides/ride_list.html", {
        "rides": rides
    })


@login_required
def ride_detail(request, ride_id):
    if request.user.role != "customer":
        return render(request, "rides/access_denied.html")

    ride = get_object_or_404(
        Ride,
        id=ride_id,
        customer=request.user.customer_profile
    )

    return render(request, "rides/ride_detail.html", {
        "ride": ride
    })


@login_required
@require_GET
def ride_detail_data(request, ride_id):
    if request.user.role != "customer":
        return JsonResponse({"error": "Access denied"}, status=403)

    ride = get_object_or_404(
        Ride,
        id=ride_id,
        customer=request.user.customer_profile
    )

    driver_data = None

    if ride.driver:
        car = getattr(ride.driver, "car", None)

        driver_data = {
            "name": str(ride.driver),
            "car": None,
        }

        if car:
            driver_data["car"] = {
                "brand": car.brand,
                "model": car.model,
                "color": car.color,
                "plate_number": car.plate_number,
                "year": car.year,
            }

    return JsonResponse({
        "status": ride.status,
        "status_display": ride.get_status_display(),
        "driver": driver_data,
        "updated_at": ride.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    })


@login_required
def update_ride(request, ride_id):
    if request.user.role != "customer":
        return render(request, "rides/access_denied.html")

    ride = get_object_or_404(
        Ride,
        id=ride_id,
        customer=request.user.customer_profile
    )

    if ride.status != Ride.Status.PENDING:
        return render(request, "rides/ride_not_editable.html", {
            "ride": ride
        })

    if request.method == "POST":
        form = RideCreateForm(request.POST, instance=ride)

        if form.is_valid():
            try:
                ride = form.save(commit=False)

                distance, duration = calculate_route_metrics(
                    ride.pickup_latitude,
                    ride.pickup_longitude,
                    ride.destination_latitude,
                    ride.destination_longitude,
                )

                ride.distance_km = distance
                ride.duration_minutes = duration
                ride.fare = calculate_fare(distance, duration)

                ride.save()

                return redirect("ride_detail", ride_id=ride.id)

            except ValueError as error:
                form.add_error(None, str(error))

    else:
        form = RideCreateForm(instance=ride)

    return render(request, "rides/update_ride.html", {
        "form": form,
        "ride": ride
    })



@login_required
def cancel_ride(request, ride_id):
    if request.user.role != "customer":
        return render(request, "rides/access_denied.html")

    ride = get_object_or_404(
        Ride,
        id=ride_id,
        customer=request.user.customer_profile
    )

    if request.method == "POST":
        if ride.status == Ride.Status.PENDING:
            ride.status = Ride.Status.CANCELLED
            ride.save()

        return redirect("ride_detail", ride_id=ride.id)

    return render(request, "rides/cancel_ride.html", {
        "ride": ride
    })


@require_GET
def fare_preview(request):
    try:
        distance = Decimal(request.GET.get("distance", ""))
        duration = Decimal(request.GET.get("duration", ""))

        if (
            not distance.is_finite()
            or not duration.is_finite()
            or distance <= 0
            or duration <= 0
        ):
            raise ValueError

        fare = calculate_fare(distance, duration)

        return JsonResponse({
            "fare": fare,
            "currency": "UZS",
        })

    except (InvalidOperation, ValueError, TypeError):
        return JsonResponse(
            {"error": "Noto'g'ri masofa yoki vaqt"},
            status=400
        )