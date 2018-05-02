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
    class Meta:
        model = ParkingSpace
        fields = ('id', 'address', 'latitude', 'longitude', 'features', 'description', 'size', 'available_spaces',)


class ReservationSerializer(serializers.ModelSerializer):
    from accounts.serializers import CarMinimalSerializer

    car = CarField(write_only=True)
    car_detail = CarMinimalSerializer(source='car', read_only=True)
    car_url = serializers.HyperlinkedRelatedField(
        source='car',
        read_only=True,
        view_name='car-detail')

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
        print("&&&&&&&&&&&&&&&&&&")
        print(validated_data)
        print("&&&&&&&&&&&&&&&&&&")
        car = validated_data.pop('car')
        reservation = Reservation.objects.create(**validated_data, car=car)
        return reservation

    def validate_car(self, value):
        """
        ensure that the user creating a reservation owns the car specified
        in the car field.
        """
        if value.customer != self.context['request'].user.customer:
            raise serializers.ValidationError("Current user must own specified car.")
        return value
