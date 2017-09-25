from django.contrib import admin

from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation


class FixedAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('parking_space', 'get_start', 'get_end', 'get_pricing')
    ordering = ('start_datetime',)

    def get_start(self, obj):
        return obj.start_datetime
    get_start.short_description = 'start'

    def get_end(self, obj):
        return obj.end_datetime
    get_end.short_description = 'end'

    def get_pricing(self, obj):
        return '$' + str((obj.pricing * 12)/100) + ' / hr'
    get_pricing.short_description = 'price'


class RepeatingAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('parking_space', 'start_time', 'end_time', 'repeating_days', 'get_pricing')

    def get_pricing(self, obj):
        return '$' + str((obj.pricing * 12)/100) + ' / hr'
    get_pricing.short_description = 'price'


admin.site.register(ParkingSpace)
admin.site.register(FixedAvailability, FixedAvailabilityAdmin)
admin.site.register(RepeatingAvailability, RepeatingAvailabilityAdmin)
admin.site.register(Reservation)