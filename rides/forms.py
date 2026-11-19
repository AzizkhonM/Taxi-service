from django import forms
from .models import Ride

class RideCreateForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            "pickup_address",
            "pickup_latitude",
            "pickup_longitude",
            "destination_address",
            "destination_latitude",
            "destination_longitude",
        ]
        widgets = {
            "pickup_latitude": forms.HiddenInput(),
            "pickup_longitude": forms.HiddenInput(),
            "destination_latitude": forms.HiddenInput(),
            "destination_longitude": forms.HiddenInput(),
        }