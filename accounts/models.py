from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Sum
from django.db.models.query import Q

import datetime
import pytz

from decouple import config
from enum import Enum

from .managers import UserManager

import stripe
stripe.api_key = config('STRIPE_SECRET_KEY')


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=30, blank=False)
    last_name = models.CharField('last name', max_length=30, blank=False)
    phone_number = models.CharField('phone number', max_length=20, blank=False, unique=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        is_initial_save = False
        if self.pk is None:
            is_initial_save = True

        super().save(*args, **kwargs)
        if is_initial_save:
            stripe_customer = stripe.Customer.create(
                description="Customer for " + self.first_name + " " + self.last_name,
                email=self.email,
                metadata={'user_id': self.pk}
            )
            Customer.objects.create(user=self, stripe_customer_id=stripe_customer.id)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def is_host(self):
        try:
            self.host
        except ObjectDoesNotExist:
            return False
        return True

    def is_customer(self):
        try:
            self.customer
        except ObjectDoesNotExist:
            return False
        return True


class Address(models.Model):
    address1 = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    code = models.CharField(max_length=15)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        address_string = self.address1
        if self.address2 is not None:
            address_string += ", " + self.address2

        return address_string + ", {}, {} {}".format(self.city, self.state, self.code)


class Customer(models.Model):

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    stripe_customer_id = models.CharField(max_length=30, unique=True, null=False)

    def reservations(self):
        from parking.models import Reservation
        return Reservation.objects.filter(vehicle__customer=self)

    def __str__(self):
        return "Customer: %s %s" % (self.user.first_name, self.user.last_name)


class Host(models.Model):

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True)
    host_since = models.DateField(auto_now_add=True)

    venmo_email = models.EmailField(unique=True, null=True, blank=True)
    venmo_phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    address = models.OneToOneField(Address, null=True, blank=True, on_delete=models.PROTECT)

    def reservations(self):
        from parking.models import ParkingSpace, Reservation
        parking_space_set = ParkingSpace.objects.filter(host=self)

        # TODO: figure out why self.parkingspace_set doesn't work

        host_reservations = Reservation.objects.none()

        for parking_space in parking_space_set:
            # merge reservations of each parking space
            host_reservations = host_reservations | parking_space.reservations()

        return host_reservations

    @property
    def available_balance(self):
        from parking.models import Reservation

        earnings = Reservation.objects.filter(
            Q(fixed_availability__parking_space__host=self) |
            Q(repeating_availability__parking_space__host=self)).filter(
            paid_out=False).filter(
            end_datetime__lt=datetime.datetime.now(pytz.utc)).filter(
            cancelled=False).aggregate(Sum('host_income'))
        return earnings['host_income__sum'] or 0

    def save(self, *args, **kwargs):
        if self.venmo_email is None:
            self.venmo_email = self.user.email
        super(Host, self).save()

    def __str__(self):
        return "Host: %s %s" % (self.user.first_name, self.user.last_name)


class VehicleSize(Enum):
    Motorcycle = 1
    Compact = 2
    Mid_sized = 3
    Large = 4
    Oversized = 5


VEHICLE_SIZES = (
    (VehicleSize.Motorcycle.value, "Motorcycle"),
    (VehicleSize.Compact.value, "Compact"),
    (VehicleSize.Mid_sized.value, "Mid-sized"),
    (VehicleSize.Large.value, "Large"),
    (VehicleSize.Oversized.value, "Oversized"),
)


class Vehicle(models.Model):

    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    color = models.CharField(max_length=25)
    year = models.CharField(max_length=25)
    make = models.CharField(max_length=25)
    model = models.CharField(max_length=25)
    size = models.PositiveIntegerField(choices=VEHICLE_SIZES)
    license_plate = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return "Vehicle: %s - %s %s %s %s" % (
            self.license_plate, self.color, self.year, self.make, self.model)
