from rest_framework import serializers

from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation


class ParkingSpaceSerializer(serializers.HyperlinkedModelSerializer):
    fixedavailability_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='fixedavailability-detail',
        read_only=True)
    repeatingavailability_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='repeatingavailability-detail',
        read_only=True)

    class Meta:
        model = ParkingSpace
        fields = '__all__'


class FixedAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = FixedAvailability
        fields = '__all__'


class RepeatingAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

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
