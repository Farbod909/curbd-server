from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.query import Q
from rest_framework import serializers

import datetime
from decouple import config
import pytz

from .models import Customer, Host, Vehicle

import stripe
stripe.api_key = config('STRIPE_SECRET_KEY')


class UserListSerializer(serializers.ModelSerializer):
    """
    Standard User Serializer for displaying a list of users via GET.
    Allows creation of users via POST.
    """
    id = serializers.IntegerField(read_only=True)

    is_host = serializers.BooleanField()

    class Meta:
        model = get_user_model()
        exclude = ('groups', 'user_permissions',)
        read_only_fields = ('last_login', 'is_superuser', 'is_staff', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_host = validated_data.pop('is_host')
        password = validated_data.pop('password')
        user = get_user_model().objects.create(**validated_data)
        user.set_password(password)
        user.save()
        if is_host:
            Host.objects.create(user=user)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Standard User Serializer that allows viewing detail of a User instance.
    Allows deletion and editing of user attributes via DELETE, PUT, and PATCH
    """
    id = serializers.IntegerField(read_only=True)

    is_host = serializers.BooleanField(help_text="un-marking this doesn't do anything. "
                                                 "You can set is_host to true, but "
                                                 "not vice versa.")

    class Meta:
        model = get_user_model()
        exclude = ('password', 'groups', 'user_permissions',)
        read_only_fields = ('last_login', 'is_superuser', 'is_staff',)

    def update(self, instance, validated_data):
        is_host = False
        if validated_data.get('is_host'):
            is_host = validated_data.pop('is_host')

        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        if is_host:
            try:
                Host.objects.create(user=instance)
            except IntegrityError:  # user is already a host
                pass
        # POSSIBLE ADDITION: allow deleting of Host object if is_host is set to false

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)


class VehicleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='vehicle-detail')
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ('customer',)


class VehicleMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'year', 'make', 'model', 'color', 'size', 'license_plate',)


class CustomerSerializer(serializers.ModelSerializer):
    from parking.serializers import ReservationSerializer

    user = UserDetailSerializer(read_only=True)
    vehicle_set = VehicleSerializer(
        many=True,
        # view_name='vehicle-detail',
        read_only=True)
    reservations = ReservationSerializer(
        many=True,
        read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


class HostSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    parkingspace_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='parkingspace-detail',
        read_only=True)

    # sum of all of host's income from past and future reservations
    total_earnings = serializers.SerializerMethodField()

    # sum of all of host's income that has not been paid out yet
    current_balance = serializers.SerializerMethodField()

    # sum of all of host's income that has not been paid out and is available for pay out
    available_balance = serializers.SerializerMethodField()

    class Meta:
        model = Host
        fields = '__all__'

    def get_total_earnings(self, host):
        from parking.models import Reservation

        earnings = Reservation.objects.filter(
            Q(fixed_availability__parking_space__host=host) |
            Q(repeating_availability__parking_space__host=host)).filter(cancelled=False).aggregate(Sum('host_income'))
        return earnings['host_income__sum'] or 0

    def get_current_balance(self, host):
        from parking.models import Reservation

        earnings = Reservation.objects.filter(
            Q(fixed_availability__parking_space__host=host) |
            Q(repeating_availability__parking_space__host=host)).filter(paid_out=False, cancelled=False).aggregate(Sum('host_income'))

        return earnings['host_income__sum'] or 0

    def get_available_balance(self, host):
        from parking.models import Reservation

        earnings = Reservation.objects.filter(
            Q(fixed_availability__parking_space__host=host) |
            Q(repeating_availability__parking_space__host=host)).filter(
            paid_out=False, cancelled=False).filter(
            end_datetime__lt=datetime.datetime.now(pytz.utc)).aggregate(Sum('host_income'))
        return earnings['host_income__sum'] or 0
