from django.contrib import admin
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation


class FixedAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('parking_space', 'start_datetime', 'end_datetime', 'pricing')
    ordering = ('start_datetime',)


admin.site.register(ParkingSpace)
admin.site.register(FixedAvailability, FixedAvailabilityAdmin)
admin.site.register(RepeatingAvailability)
admin.site.register(Reservation)