from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=30, blank=False)
    last_name = models.CharField('last name', max_length=30, blank=False)
    phone_number = models.CharField('phone number', max_length=15, blank=False, unique=True)
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


class Customer(models.Model):

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def reservations(self):
        from parking.models import Reservation
        return Reservation.objects.filter(car__customer=self)

    def __str__(self):
        return "Customer: %s %s" % (self.user.first_name, self.user.last_name)


class Host(models.Model):

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return "Host: %s %s" % (self.user.first_name, self.user.last_name)


class Car(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    color = models.CharField(max_length=25)
    year = models.CharField(max_length=25)
    make = models.CharField(max_length=25)
    model = models.CharField(max_length=25)
    license_plate = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return "Car: %s - %s %s %s %s" % (
            self.license_plate, self.color, self.year, self.make, self.model)


class Rating(models.Model):

    value = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
