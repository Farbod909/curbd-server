from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from enum import Enum
import calendar
import datetime
import pytz

from .fields import ChoiceArrayField
from accounts.models import Car, Host


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

    available_spaces = models.PositiveIntegerField(
        "Number of spaces available",
        help_text="NOTE: Each individual parking space should be positioned such that "
                  "each car can arrive and leave independent of other cars currently "
                  "parked at that location. If this is not possible, please enter "
                  "'1' as the number of spaces available.",
        default=1)
    size = models.PositiveIntegerField(
        "Max supported automobile size",
        choices=VEHICLE_SIZES,
        help_text="This is the maximum vehicle size the parking space can support")
    features = ChoiceArrayField(
        models.CharField(max_length=50, choices=FEATURES),
        blank=True,
        help_text="A list of features e.g. EV charging, shade, etc.")

    address = models.CharField(
        "Street address",
        max_length=50,
        help_text="e.g. '123 Robertson'")
    description = models.CharField(
        max_length=100, blank=True,
        help_text="Any description that will help customers find the parking spot")

    # TODO: parking space photos

    def unreserved_spaces(self, start_datetime, end_datetime) -> int:
        num = self.available_spaces

        for fa in self.fixedavailability_set.all():
            if fa.is_reserved(start_datetime, end_datetime):
                num -= 1

        for ra in self.repeatingavailability_set.all():
            if ra.is_reserved(start_datetime, end_datetime):
                num -= 1

        return num

    def __str__(self):
        return self.address


class FixedAvailability(models.Model):

    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    pricing = models.PositiveIntegerField(
        default=15,
        help_text="The cost (in U.S. cents) of parking at the space for 5 minutes")
    # This is the price the CUSTOMER pays (not what the HOST earns)

    class Meta:
        verbose_name_plural = 'fixed availabilities'

    def get_duration(self):
        """ get duration of fixed availability in hours """
        delta = self.end_datetime - self.start_datetime
        return delta.days*24 + delta.seconds/3600

    def get_weekday_span(self):
        def get_weekday_span_between(weekday1, weekday2):
            weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            weekday1_index = weekdays.index(weekday1)
            weekday2_index = weekdays.index(weekday2)

            if weekday1_index == weekday2_index:
                return [weekday1]
            elif weekday1_index < weekday2_index:
                return weekdays[weekday1_index:weekday2_index + 1]
            else:
                return weekdays[weekday1_index:] + weekdays[:weekday2_index + 1]

        return get_weekday_span_between(
                calendar.day_name[timezone.localtime(self.start_datetime).weekday()][:3],
                calendar.day_name[timezone.localtime(self.end_datetime).weekday()][:3])

    def check_end_comes_after_start(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError("Availability end time must come after start time")

    def check_ends_after_current_time(self):
        if self.end_datetime < timezone.now():
            raise ValidationError("Availability end time must come after current time")

    def check_overlap_with_fixed_availabilities(self):
        fixed_availabilities = FixedAvailability.objects.filter(parking_space=self.parking_space)

        if self.pk is not None:
            fixed_availabilities = fixed_availabilities.exclude(pk=self.pk)

        for fixed_availability in fixed_availabilities:
            if (self.start_datetime <= fixed_availability.end_datetime) and (self.end_datetime >= fixed_availability.start_datetime):
                raise ValidationError("Overlaps with other availability")

    def check_overlap_with_repeating_availabilities(self):
        repeating_availabilities = RepeatingAvailability.objects.filter(parking_space=self.parking_space)

        if self.pk is not None:
            repeating_availabilities = repeating_availabilities.exclude(pk=self.pk)

        fixed_availability = self

        # 168 hours is equivalent to one week. If the duration of the
        # fixed availability encompasses one week or longer, no combination
        # of repeating availabilities is possible without overlap.
        if fixed_availability.get_duration() >= 168:
            raise ValidationError("Overlaps with other availability")
        else:
            weekday_span = self.get_weekday_span()

        for repeating_availability in repeating_availabilities:

            # All of the days in weekday_span that aren't the first and last days
            # of the fixed availability, are fully reserved. Therefore, if any of
            # the repeating days are present in this list (weekday_span[1:-1]),
            # there is an overlap.
            if list(set(repeating_availability.repeating_days) & set(weekday_span[1:-1])):
                raise ValidationError("Overlaps with other availability")

            # Now we check if the fixed availability's start day or end day is
            # the same weekday as one of the repeating availability days. If so,
            # we check to see if it overlaps at any time.
            if weekday_span[0] in repeating_availability.repeating_days:
                if repeating_availability.start_time < fixed_availability.start_datetime.time() < repeating_availability.end_time:
                    raise ValidationError("Overlaps with other availability")

            if weekday_span[-1] in repeating_availability.repeating_days:
                if repeating_availability.start_time < fixed_availability.end_datetime.time() < repeating_availability.end_time:
                    raise ValidationError("Overlaps with other availability")

    def save(self, *args, **kwargs):
        self.check_end_comes_after_start()
        self.check_ends_after_current_time()
        self.check_overlap_with_fixed_availabilities()
        self.check_overlap_with_repeating_availabilities()

        super(FixedAvailability, self).save(*args, **kwargs)

    def is_reserved(self, start_datetime, end_datetime):
        for reservation in self.reservation_set.all():
            if reservation.overlaps_with(start_datetime, end_datetime):
                return True

        return False

    def __str__(self):
        return "%s: %s - %s" % (
            self.parking_space,
            timezone.localtime(self.start_datetime).strftime("%Y-%m-%d %H:%M"),
            timezone.localtime(self.end_datetime).strftime("%Y-%m-%d %H:%M"))


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

    parking_space = models.ForeignKey(
        ParkingSpace, on_delete=models.CASCADE)

    start_time = models.TimeField()
    end_time = models.TimeField()
    repeating_days = ChoiceArrayField(
        models.CharField(max_length=15, choices=DAYS_OF_THE_WEEK))

    pricing = models.PositiveIntegerField(
        default=15,
        help_text="The cost (in U.S. cents) of parking at the space for 5 minutes")
    # This is the price the CUSTOMER pays (not what the HOST earns)

    class Meta:
        verbose_name_plural = 'repeating availabilities'

    def check_end_comes_after_start(self):
        if self.start_time > self.end_time:
            raise ValidationError("Availability end time must come after start time")

    def check_overlap_with_fixed_availabilities(self):
        fixed_availabilities = FixedAvailability.objects.filter(parking_space=self.parking_space)

        if self.pk is not None:
            fixed_availabilities = fixed_availabilities.exclude(pk=self.pk)

        repeating_availability = self

        for fixed_availability in fixed_availabilities:
            if fixed_availability.get_duration() >= 168:
                raise ValidationError("Overlaps with other availability")

            fixed_availability_weekday_span = fixed_availability.get_weekday_span()

            if list(set(repeating_availability.repeating_days) & set(fixed_availability_weekday_span[1:-1])):
                raise ValidationError("Overlaps with other availability")

            if fixed_availability_weekday_span[0] in repeating_availability.repeating_days:
                if repeating_availability.start_time < fixed_availability.start_datetime.time() < repeating_availability.end_time:
                    raise ValidationError("Overlaps with other availability")

            if fixed_availability_weekday_span[-1] in self.repeating_days:
                if repeating_availability.start_time < fixed_availability.end_datetime.time() < repeating_availability.end_time:
                    raise ValidationError("Overlaps with other availability")

    def check_overlap_with_repeating_availabilities(self):
        repeating_availabilities = RepeatingAvailability.objects.filter(parking_space=self.parking_space)

        if self.pk is not None:
            repeating_availabilities = repeating_availabilities.exclude(pk=self.pk)

        for repeating_availability in repeating_availabilities:
            if list(set(self.repeating_days) & set(repeating_availability.repeating_days)):
                if (self.start_time <= repeating_availability.end_time) and (self.end_time >= repeating_availability.start_time):
                    raise ValidationError("Overlaps with other availability")

    def save(self, *args, **kwargs):
        self.check_end_comes_after_start()
        self.check_overlap_with_fixed_availabilities()
        self.check_overlap_with_repeating_availabilities()

        super(RepeatingAvailability, self).save(*args, **kwargs)

    def is_reserved(self, start_datetime, end_datetime):
        for reservation in self.reservation_set.all():
            if reservation.overlaps_with(start_datetime, end_datetime):
                return True

        return False

    def __str__(self):
        repeating_days = ', '.join(self.repeating_days)
        return '%s: Every %s, %s - %s' % (
            self.parking_space,
            repeating_days,
            self.start_time.strftime("%H:%M"),
            self.end_time.strftime("%H:%M"))


class Reservation(models.Model):

    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    for_repeating = models.BooleanField(editable=False)
    # determines if this reservation is for a
    # RepeatingAvailability or a FixedAvailability

    fixed_availability = models.ForeignKey(
        FixedAvailability, on_delete=models.PROTECT, blank=True, null=True)
    repeating_availability = models.ForeignKey(
        RepeatingAvailability, on_delete=models.PROTECT, blank=True, null=True)

    def set_for_repeating_field(self):
        if self.for_repeating is None:
            if self.repeating_availability is None:
                self.for_repeating = False
            else:
                self.for_repeating = True

    def check_end_comes_after_start(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError("Reservation end time must come after start time")

    def check_start_and_end_within_availability_bounds(self):
        if self.for_repeating:
            weekday = calendar.day_name[self.start_datetime.weekday()][:3]  # first 3 letters of weekday e.g. 'Mon'
            if weekday not in self.repeating_availability.repeating_days:
                raise ValidationError('Reservation is not a valid weekday')
            if self.start_datetime.time() < self.repeating_availability.start_time or \
                    self.end_datetime.time() > self.repeating_availability.end_time:
                raise ValidationError("Start and end time of reservation is not within "
                                      "bounds of start and end time of availability")
        else:
            if self.start_datetime < self.fixed_availability.start_datetime or \
                    self.end_datetime > self.fixed_availability.end_datetime:
                raise ValidationError("Start and end time of reservation is not within "
                                      "bounds of start and end time of availability")

    def check_reservation_overlap(self):
        if self.for_repeating:
            parking_space = self.repeating_availability.parking_space
        else:
            parking_space = self.fixed_availability.parking_space

        reservations = Reservation.objects.filter(
            Q(repeating_availability__parking_space=parking_space) |
            Q(fixed_availability__parking_space=parking_space))

        if self.pk is not None:
            reservations = reservations.exclude(pk=self.pk)

        for reservation in reservations:
            if self.overlaps_with(reservation.start_datetime, reservation.end_datetime):
                raise ValidationError("Overlaps with other reservation")

    def save(self, *args, **kwargs):
        self.set_for_repeating_field()  # set the 'for_repeating' field
        self.check_end_comes_after_start()  # make sure reservation end time comes after its start time
        self.check_start_and_end_within_availability_bounds()
        # make sure reservation start and end time are within
        # start and end time of its availability
        self.check_reservation_overlap()

        super(Reservation, self).save(*args, **kwargs)

    def overlaps_with(self, start_datetime, end_datetime):
        return (self.start_datetime <= end_datetime) and (self.end_datetime >= start_datetime)

    def __str__(self):
        if self.for_repeating:
            parking_space = self.repeating_availability.parking_space
        else:
            parking_space = self.fixed_availability.parking_space

        return "%s @ %s: %s - %s" % (
                self.car,
                parking_space,
                timezone.localtime(self.start_datetime).strftime("%H:%M on %b %d, %Y"),
                timezone.localtime(self.end_datetime).strftime("%H:%M on %b %d, %Y"))
