from django import forms

from accounts.models import Car
from .models import ParkingSpace, Reservation
from accounts.models import VEHICLE_SIZES


class ParkingSpaceCreationForm(forms.Form):
    address = forms.CharField()
    size = forms.ChoiceField(
        choices=VEHICLE_SIZES,
        help_text="This is the maximum vehicle size the parking space can support")
    features = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=ParkingSpace.FEATURES,
        help_text="A list of features e.g. EV charging, shade, etc.")
    description = forms.CharField(widget=forms.Textarea)


class ReservationCreationForm(forms.ModelForm):
    parking_space = forms.ModelChoiceField(queryset=ParkingSpace.objects.all())

    class Meta:
        model = Reservation
        fields = ('car', 'start_datetime', 'end_datetime',)

    def __init__(self, request, *args, **kwargs):
        super(ReservationCreationForm, self).__init__(*args, **kwargs)

        # limit the cars queryset to the currently logged-in user's car set
        self.fields['car'].queryset = Car.objects.filter(customer__user=request.user)
