from django.db import models
from django.contrib.postgres.fields import ArrayField
from .fields import ChoiceArrayField
from accounts.models import Car, Host


class ParkingSpace(models.Model):

    AUTOMOBILE_SIZES = (
        (1, "Motorcycle"),
        (2, "Compact"),
        (3, "Mid-sized"),
        (4, "Large"),
        (5, "Oversized"),
    )

    FEATURES = (
        ("EV Charging", "EV Charging"),
        ("Lit", "Lit"),
        ("Covered", "Covered"),
        ("Guarded", "Guarded"),
    )

    host = models.ForeignKey(
        Host, on_delete=models.CASCADE,
        help_text="The host that the parking space belongs to")

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    size = models.PositiveIntegerField(
        "Max supported automobile size",
        choices=AUTOMOBILE_SIZES,
        help_text="This is the maximum vehicle size the parking space can support")
    features = ChoiceArrayField(
        models.CharField(max_length=50, choices=FEATURES),
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
        return "%s: %s -> %s" % (
            self.parking_space,
            self.start_datetime.strftime("%Y-%m-%d %H:%M"),
            self.end_datetime.strftime("%Y-%m-%d %H:%M"))


class RepeatingAvailability(models.Model):

    DAYS_OF_THE_WEEK = (
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    repeating_days = ArrayField(
        models.IntegerField(choices=DAYS_OF_THE_WEEK))

    parking_space = models.ForeignKey(
        ParkingSpace, on_delete=models.CASCADE)
    pricing = models.PositiveIntegerField(
        default=15, help_text="The cost of parking at the space for 5 minutes")

    class Meta:
        verbose_name_plural = 'repeating availabilities'


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
        return "%s @ %s: %s -> %s" % (
            self.car
            self.fixed_availability.parking_space,
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M"))

