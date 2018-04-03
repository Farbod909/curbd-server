from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Customer, Host, Car


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Standard User Serializer that does not allow editing of certain
    attributes such as is_superuser, is_staff, etc.
    """
    host = serializers.HyperlinkedRelatedField(view_name='host-detail', read_only=True)
    customer = serializers.HyperlinkedRelatedField(view_name='customer-detail', read_only=True)
    is_host = serializers.BooleanField(write_only=True)

    class Meta:
        model = get_user_model()
        exclude = ('groups', 'user_permissions',)
        read_only_fields = ('last_login', 'is_superuser', 'is_staff',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_host = validated_data.pop('is_host')
        user = get_user_model().objects.create(**validated_data)
        Customer.objects.create(user=user)
        if is_host:
            Host.objects.create(user=user)
        return user


class HighPermissionUserSerializer(UserSerializer):
    """
    This Serializer class allows editing of the is_staff attribute of User.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ('last_login', 'is_superuser',)


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    car_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='car-detail',
        read_only=True,
        lookup_field='license_plate')
    reservations = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


class HostSerializer(serializers.HyperlinkedModelSerializer):
    parkingspace_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='parkingspace-detail',
        read_only=True)

    class Meta:
        model = Host
        fields = '__all__'


class CarSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='car-detail',
        lookup_field='license_plate')
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = Car
        fields = '__all__'
