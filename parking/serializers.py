from rest_framework import serializers

from .models import ParkingSpace


class ParkingSpaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParkingSpace
        fields = '__all__'
