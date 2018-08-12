from rest_framework import serializers

from .serializer_fields import StringArrayField, VehicleField, ParkingSpaceField
from .models import ParkingSpace, FixedAvailability, RepeatingAvailability, Reservation


class FixedAvailabilitySerializer(serializers.ModelSerializer):
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


class RepeatingAvailabilitySerializer(serializers.ModelSerializer):
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


class ParkingSpaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='parkingspace-detail')
    fixedavailability_set = FixedAvailabilitySerializer(
        many=True, read_only=True)
    repeatingavailability_set = RepeatingAvailabilitySerializer(
        many=True, read_only=True)
    # reservations = ReservationSerializer(
    #     many=True,
    #     read_only=True)
    features = StringArrayField()
    # TODO: add validation for features

    class Meta:
        model = ParkingSpace
        fields = '__all__'
        read_only_fields = ('host',)


class ParkingSpaceMinimalSerializer(serializers.ModelSerializer):
    features = StringArrayField()
    # TODO: add validation for features

    class Meta:
        model = ParkingSpace
        fields = ('id', 'name', 'latitude', 'longitude', 'features', 'instructions', 'size', 'available_spaces',)


class ReservationSerializer(serializers.ModelSerializer):
    from accounts.serializers import VehicleMinimalSerializer, UserDetailSerializer

    vehicle = VehicleField(write_only=True)
    vehicle_detail = VehicleMinimalSerializer(source='vehicle', read_only=True)
    vehicle_url = serializers.HyperlinkedRelatedField(
        source='vehicle',
        read_only=True,
        view_name='vehicle-detail')

    reserver = UserDetailSerializer(source='vehicle.customer.user', read_only=True)

    parking_space_id = serializers.PrimaryKeyRelatedField(queryset=ParkingSpace.objects.all(), write_only=True)
    parking_space = ParkingSpaceMinimalSerializer(read_only=True)
    parking_space_url = serializers.HyperlinkedRelatedField(
        source='parking_space',
        read_only=True,
        view_name='parkingspace-detail')

    class Meta:
        model = Reservation
        fields = '__all__'
        # exclude = ('for_repeating',)
        read_only_fields = ('fixed_availability', 'repeating_availability',)
        depth = 1

    def create(self, validated_data):
        vehicle = validated_data.pop('vehicle')
        reservation = Reservation.objects.create(**validated_data, vehicle=vehicle)
        return reservation

    def validate_vehicle(self, value):
        """
        ensure that the user creating a reservation owns the vehicle specified
        in the vehicle field.
        """
        if value.customer != self.context['request'].user.customer:
            raise serializers.ValidationError("Current user must own specified vehicle.")
        return value
