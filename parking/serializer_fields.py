from rest_framework.serializers import ListField, HyperlinkedRelatedField, PrimaryKeyRelatedField


class StringArrayField(ListField):
    """
    String representation of an array field.
    """
    def to_representation(self, obj):
        obj = super().to_representation(obj)
        # convert list to string
        return ", ".join([str(element) for element in obj])

    def to_internal_value(self, data):
        data = data[0].split(", ")  # convert string to list
        return super().to_internal_value(data)


class CarField(PrimaryKeyRelatedField):
    """
    Field that limits the queryset of the cars to the cars
    owned by the current user
    """

    def get_queryset(self):
        # TODO: limit queryset only if user is not admin
        from accounts.models import Car
        return Car.objects.filter(customer__user=self.context['request'].user)  # TODO: determine an order_by


class ParkingSpaceField(HyperlinkedRelatedField):
    """
    Field that limits the queryset of the parking spaces
    to those owned by the current user
    """
    view_name = 'parkingspace-detail'

    def get_queryset(self):
        # TODO: limit queryset only if user is not admin
        from parking.models import ParkingSpace
        return ParkingSpace.objects.filter(host__user=self.context['request'].user)  # TODO: determine an order_by
