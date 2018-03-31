from rest_framework import permissions


class IsAdminOrIsParkingSpaceOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the parking space owner to edit
    the parking space.
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.host.user == request.user


class HostsCanCreateAndStaffCanRead(permissions.BasePermission):
    """
    Custom permission to only allow hosts to create parking spaces.
    Only staff can read.
    """
    def has_permission(self, request, view):

        if request.method == 'POST':
            try:
                return request.user.is_host()
            except AttributeError:  # AnonymousUser (when no user is logged in) has no attribute is_host
                return False

        return request.user.is_staff


class IsAdminOrIsOwnerOfParkingSpaceOfAvailabilityOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the owner of the parking
    space of the availability to edit
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.parking_space.host.user == request.user


class IsAdminOrIsReservationOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the customer who reserved the
    parking space to edit
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.car.customer.user == request.user
