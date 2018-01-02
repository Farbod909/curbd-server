from django import forms
from .models import ParkingSpace


class ParkingSpaceCreationForm(forms.Form):
    address = forms.CharField()
    size = forms.ChoiceField(
        choices=ParkingSpace.VEHICLE_SIZES,
        help_text="This is the maximum vehicle size the parking space can support")
    features = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=ParkingSpace.FEATURES,
        blank=True,
        help_text="A list of features e.g. EV charging, shade, etc.")
    description = forms.CharField(widget=forms.Textarea)
