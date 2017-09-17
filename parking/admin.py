from django.contrib import admin
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation

admin.site.register(ParkingSpace)
admin.site.register(FixedAvailability)
admin.site.register(RepeatingAvailability)
admin.site.register(Reservation)