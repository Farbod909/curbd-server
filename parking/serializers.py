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
    id = serializers.IntegerField(read_only=True)
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
    car_url = serializers.HyperlinkedRelatedField(
        source='car',
        read_only=True,
        view_name='car-detail')

    parking_space = serializers.PrimaryKeyRelatedField(queryset=ParkingSpace.objects.all())
    parking_space_url = serializers.HyperlinkedRelatedField(
        source='parking_space',
        read_only=True,
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


