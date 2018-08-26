from rest_framework.serializers import ListField, HyperlinkedRelatedField, PrimaryKeyRelatedField


class StringArrayField(ListField):
    """
    String representation of an array field.
    """
    def to_representation(self, obj):
        obj = super().to_representation(obj)

        # uncomment this if you want the REST API to show [] instead of ""
        # for parking spaces with an empty features array.
        # if not obj:
        #     return []

        # convert list to string
        return ", ".join([str(element) for element in obj])

    def to_internal_value(self, data):
        if data:  # if data is non-empty
            data = data[0].split(", ")  # convert string to list
        return super().to_internal_value(data)


class VehicleField(PrimaryKeyRelatedField):
    """
    Field that limits the queryset of the vehicles to the vehicles
    owned by the current user
    """

    source = 'vehicle'

    def get_queryset(self):
        # TODO: limit queryset only if user is not admin
        from accounts.models import Vehicle
        return Vehicle.objects.filter(customer__user=self.context['request'].user)  # TODO: determine an order_by


class ParkingSpaceField(PrimaryKeyRelatedField):
    """
    Field that limits the queryset of the parking spaces
    to those owned by the current user
    """
    view_name = 'parkingspace-detail'

    def get_queryset(self):
        # TODO: limit queryset only if user is not admin
        from parking.models import ParkingSpace
        return ParkingSpace.objects.filter(host__user=self.context['request'].user)  # TODO: determine an order_by
