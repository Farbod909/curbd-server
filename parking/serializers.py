from rest_framework import serializers

from .serializer_fields import StringArrayField, CarField, ParkingSpaceField
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation, Car


class FixedAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    parking_space = ParkingSpaceField()
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)

    class Meta:
        model = FixedAvailability
        fields = '__all__'

    def validate_parking_space(self, value):
        """
        ensure that the user creating an availability owns the parking space
        specified in the parking_space field.
        """
        try:
            if self.context['request'].user.host != value.host:
                raise serializers.ValidationError("Current user must own specified parking space.")
        except AttributeError:  # user.host doesn't exist
            raise serializers.ValidationError("Current user must own specified parking space.")

        return value


class RepeatingAvailabilitySerializer(serializers.HyperlinkedModelSerializer):
    parking_space = ParkingSpaceField()
    reservation_set = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='reservation-detail',
        read_only=True)
    repeating_days = StringArrayField()  # TODO: fix this and add validation

    class Meta:
        model = RepeatingAvailability
        fields = '__all__'

    def validate_parking_space(self, value):
        """
        ensure that the user creating an availability owns the parking space
        specified in the parking_space field.
        """
        if self.context['request'].user.host != value.host:
            raise serializers.ValidationError("Current user must own specified parking space.")
        return value


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
    car = CarField()
    parking_space = serializers.HyperlinkedRelatedField(
        queryset=ParkingSpace.objects.all(),
        view_name='parkingspace-detail')

    class Meta:
        model = Reservation
        exclude = ('for_repeating',)
        read_only_fields = ('fixed_availability', 'repeating_availability',)

    def validate_car(self, value):
        """
        ensure that the user creating a reservation owns the car specified
        in the car field.
        """
        if value.customer != self.context['request'].user.customer:
            raise serializers.ValidationError("Current user must own specified car.")
        return value


