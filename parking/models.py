from django.db import models
from accounts.models import Customer, Host


class ParkingSpace(models.Model):

    host = models.ForeignKey(Host, on_delete=models.CASCADE)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    features = models.ArrayField(models.CharField())
    address = models.CharField(max_length=50)  # The address will be stored as "<number> <street>" e.g. "123 Robertson"

    description = models.CharField(max_length=50, null=True)


class FixedAvailability(models.Model):

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)

    # TODO: pricing


class RepeatingAvailability(models.Model):

    DAYS_OF_THE_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    start_time = models.TimeField()
    end_time = models.TimeField()
    repeating_days = models.ArrayField(models.CharField(choices=DAYS_OF_THE_WEEK))

    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)

    # TODO: pricing


class Reservation(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    start_time = models.TimeField()
    end_time = models.TimeField()

    for_repeating = models.BooleanField()
    # determines if this reservation is for a
    # RepeatingAvailability or a FixedAvailability

    fixed_availability = models.ForeignKey(FixedAvailability, on_delete=models.CASCADE, null=True)
    repeating_availability = models.ForeignKey(RepeatingAvailability, on_delete=models.CASCADE, null=True)

    # TODO: type of car

