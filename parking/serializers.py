from rest_framework import serializers

from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation


class ParkingSpaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParkingSpace
        fields = '__all__'


class FixedAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FixedAvailability
        fields = '__all__'


class RepeatingAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RepeatingAvailability
        fields = '__all__'


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    car = serializers.HyperlinkedRelatedField(
        view_name='car-detail',
        lookup_field='license_plate',
        read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'
