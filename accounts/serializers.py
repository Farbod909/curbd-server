from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Customer, Host, Car


class UserListSerializer(serializers.ModelSerializer):
    """
    This Serializer class displays limited fields, therefore it is
    appropriate for listing User objects.
    """

    class Meta:
        model = get_user_model()
        fields = ('email', 'url',)


class UserSerializer(serializers.ModelSerializer):
    """
    Standard User Serializer that does not allow editing of sensitive
    attributes such as is_superuser, is_staff, password, etc.
    """
    is_host = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        exclude = ('id', 'password', 'groups', 'user_permissions',)
        read_only_fields = ('last_login', 'is_superuser', 'is_staff',)

    def get_is_host(self, obj):
        return obj.is_host()


class HighPermissionUserSerializer(UserSerializer):
    """
    This Serializer class allows editing of the is_staff attribute of User.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ('last_login', 'is_superuser',)


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class HostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'


class CarSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='car-detail',
        lookup_field='license_plate'
    )

    class Meta:
        model = Car
        fields = '__all__'
