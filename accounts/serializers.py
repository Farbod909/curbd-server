from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'email', 'first_name', 'last_name',
            'phone_number', 'last_login', 'date_joined',
            'is_superuser', 'is_active', 'is_staff',)
