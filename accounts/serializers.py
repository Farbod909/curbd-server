from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Customer, Host, Car
from parking.serializers import ReservationSerializer


class UserListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Standard User Serializer for displaying a list of users via GET.
    Allows creation of users via POST.
    """
    id = serializers.IntegerField(read_only=True)

    host_url = serializers.HyperlinkedRelatedField(source='host', view_name='host-detail', read_only=True)
    customer_url = serializers.HyperlinkedRelatedField(source='customer', view_name='customer-detail', read_only=True)

    host = serializers.PrimaryKeyRelatedField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    is_host = serializers.BooleanField()

    class Meta:
        model = get_user_model()
        exclude = ('groups', 'user_permissions',)
        read_only_fields = ('last_login', 'is_superuser', 'is_staff',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_host = validated_data.pop('is_host')
        password = validated_data.pop('password')
        user = get_user_model().objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Customer.objects.create(user=user)
        if is_host:
            Host.objects.create(user=user)
        return user


class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Standard User Serializer that allows viewing detail of a User instance.
    Allows deletion and editing of user attributes via DELETE, PUT, and PATCH
    """
    id = serializers.IntegerField(read_only=True)

    host_url = serializers.HyperlinkedRelatedField(source='host', view_name='host-detail', read_only=True)
    customer_url = serializers.HyperlinkedRelatedField(source='customer', view_name='customer-detail', read_only=True)

    host = serializers.PrimaryKeyRelatedField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    is_host = serializers.BooleanField()

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
            Host.objects.create(user=instance)
        # POSSIBLE ADDITION: allow deleting of Host object if is_host is set to false

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class CarSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='car-detail')
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = Car
        fields = '__all__'
        read_only_fields = ('customer',)


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    user = UserDetailSerializer(read_only=True)
    car_set = CarSerializer(
        many=True,
        # view_name='car-detail',
        read_only=True)
    reservations = ReservationSerializer(
        many=True,
        read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


class HostSerializer(serializers.HyperlinkedModelSerializer):
    user = UserDetailSerializer(read_only=True)
    parkingspace_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='parkingspace-detail',
        read_only=True)

    class Meta:
        model = Host
        fields = '__all__'

