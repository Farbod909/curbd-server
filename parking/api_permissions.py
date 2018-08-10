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


class IsHostOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow hosts to create parking spaces.
    """
    def has_permission(self, request, view):

        if request.method == 'POST':
            try:
                return request.user.is_host()
            except AttributeError:  # 'AnonymousUser' object has no attribute 'is_host'
                return False

        return True


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to create parking spaces.
    """
    def has_permission(self, request, view):

        if request.method == 'POST':
            return request.user.is_authenticated

        return True


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

        return request.user.is_superuser or obj.vehicle.customer.user == request.user


class IsCustomerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow customers to create reservations
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            return request.user.is_customer()
        except AttributeError:  # 'AnonymousUser' object has no attribute 'is_customer'
            return False
