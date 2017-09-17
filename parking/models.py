from django.db import models
from .fields import ChoiceArrayField
from accounts.models import Car, Host
from enum import Enum


class VehicleSize(Enum):
    Motorcycle = 1
    Compact = 2
    Mid_sized = 3
    Large = 4
    Oversized = 5


class ParkingSpaceFeature(Enum):
    EV_charging = "EV Charging"
    Lit = "Lit"
    Covered = "Covered"
    Guarded = "Guarded"


class Weekday(Enum):
    Sunday = 'Sun'
    Monday = 'Mon'
    Tuesday = 'Tue'
    Wednesday = 'Wed'
    Thursday = 'Thu'
    Friday = 'Fri'
    Saturday = 'Sat'


class ParkingSpace(models.Model):

    VEHICLE_SIZES = (
        (VehicleSize.Motorcycle.value, "Motorcycle"),
        (VehicleSize.Compact.value, "Compact"),
        (VehicleSize.Mid_sized.value, "Mid-sized"),
        (VehicleSize.Large.value, "Large"),
        (VehicleSize.Oversized.value, "Oversized"),
    )

    FEATURES = (
        (ParkingSpaceFeature.EV_charging.value, "EV Charging"),
        (ParkingSpaceFeature.Lit.value, "Lit"),
        (ParkingSpaceFeature.Covered.value, "Covered"),
        (ParkingSpaceFeature.Guarded.value, "Guarded"),
    )

    host = models.ForeignKey(
        Host, on_delete=models.CASCADE,
        help_text="The host that the parking space belongs to")

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    size = models.PositiveIntegerField(
        "Max supported automobile size",
        choices=VEHICLE_SIZES,
        help_text="This is the maximum vehicle size the parking space can support")
    features = ChoiceArrayField(
        models.CharField(max_length=50, choices=FEATURES),
        blank=True,
        help_text="A list of features e.g. EV charging, shade, etc.")

    address = models.CharField(
        max_length=50,
        help_text="Please store as: '[number] [street]' e.g. '123 Robertson'")
    description = models.CharField(max_length=100, blank=True)

    # TODO: parking space photos

    def __str__(self):
        return self.address


class FixedAvailability(models.Model):

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    pricing = models.PositiveIntegerField(
        default=15, help_text="The cost of parking at the space for 5 minutes")
    # This is the price the CUSTOMER pays (not what the HOST earns)

    class Meta:
        verbose_name_plural = 'fixed availabilities'

    def __str__(self):
        return "%s: %s - %s" % (
            self.parking_space,
            self.start_datetime.strftime("%Y-%m-%d %H:%M"),
            self.end_datetime.strftime("%Y-%m-%d %H:%M"))


class RepeatingAvailability(models.Model):

    DAYS_OF_THE_WEEK = (
        (Weekday.Sunday.value, 'Sunday'),
        (Weekday.Monday.value, 'Monday'),
        (Weekday.Tuesday.value, 'Tuesday'),
        (Weekday.Wednesday.value, 'Wednesday'),
        (Weekday.Thursday.value, 'Thursday'),
        (Weekday.Friday.value, 'Friday'),
        (Weekday.Saturday.value, 'Saturday'),
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    repeating_days = ChoiceArrayField(
        models.CharField(max_length=15, choices=DAYS_OF_THE_WEEK))

    parking_space = models.ForeignKey(
        ParkingSpace, on_delete=models.CASCADE)
    pricing = models.PositiveIntegerField(
        default=15, help_text="The cost of parking at the space for 5 minutes")

    class Meta:
        verbose_name_plural = 'repeating availabilities'

    def __str__(self):
        repeating_days = ', '.join(self.repeating_days)
        return '%s: Every %s, %s - %s' % (
            self.parking_space,
            repeating_days,
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M"))


class Reservation(models.Model):

    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    start_time = models.TimeField()
    end_time = models.TimeField()

    for_repeating = models.BooleanField()
    # determines if this reservation is for a
    # RepeatingAvailability or a FixedAvailability

    fixed_availability = models.ForeignKey(
        FixedAvailability, on_delete=models.PROTECT, blank=True, null=True)
    repeating_availability = models.ForeignKey(
        RepeatingAvailability, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):

        if self.for_repeating:
            parking_space = self.repeating_availability.parking_space
        else:
            parking_space = self.fixed_availability.parking_space

        return "%s @ %s: %s - %s" % (
                self.car,
                parking_space,
                self.start_time.strftime("%H:%M"),
                self.end_time.strftime("%H:%M"))
