from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .forms import RegisterForm
from drivers.models import Driver
from rides.models import Customer


def register(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                if user.role == "driver":
                    Driver.objects.create(user=user)
                else:
                    Customer.objects.create(user=user)

            login(request, user)
            return redirect("profile")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("profile")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("profile")

        return render(request, "accounts/login.html", {
            "error": "Username yoki password noto'g'ri."
        })

    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request):
    if request.user.role == "driver":
        return redirect("driver_dashboard")

    return render(request, "accounts/profile.html")