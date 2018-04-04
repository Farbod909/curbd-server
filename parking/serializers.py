from rest_framework import serializers

from .fields import StringArrayField
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation


class FixedAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = FixedAvailability
        fields = '__all__'

    def validate_parking_space(self, value):
        if self.context['request'].user.host != value.host:
            raise serializers.ValidationError("Current user must own specified parking space.")
        return value


class RepeatingAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = RepeatingAvailability
        fields = '__all__'


class ParkingSpaceSerializer(serializers.HyperlinkedModelSerializer):
    fixedavailability_set = FixedAvailabilitySerializer(
        many=True, read_only=True)
    repeatingavailability_set = RepeatingAvailabilitySerializer(
        many=True, read_only=True)
    reservations = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)
    features = StringArrayField()
    # TODO: add validation for features

    class Meta:
        model = ParkingSpace
        fields = '__all__'
        read_only_fields = ('host',)


class ReservationSerializer(serializers.HyperlinkedModelSerializer):
    car = serializers.HyperlinkedRelatedField(
        view_name='car-detail',
        lookup_field='license_plate',
        read_only=True)
    parking_space = serializers.HyperlinkedRelatedField(
        view_name='parkingspace-detail',
        read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'
