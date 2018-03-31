from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Customer, Host, Car


class UserListSerializer(serializers.ModelSerializer):
    """
    This Serializer class displays limited fields, therefore it is
    appropriate for listing User objects.
    """
    host = serializers.HyperlinkedRelatedField(view_name='host-detail', read_only=True)
    customer = serializers.HyperlinkedRelatedField(view_name='customer-detail', read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'host', 'customer', 'url',)


class UserSerializer(serializers.ModelSerializer):
    """
    Standard User Serializer that does not allow editing of sensitive
    attributes such as is_superuser, is_staff, password, etc.
    """
    host = serializers.HyperlinkedRelatedField(view_name='host-detail', read_only=True)
    customer = serializers.HyperlinkedRelatedField(view_name='customer-detail', read_only=True)

    class Meta:
        model = get_user_model()
        exclude = ('id', 'password', 'groups', 'user_permissions',)
        read_only_fields = ('last_login', 'is_superuser', 'is_staff',)


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
