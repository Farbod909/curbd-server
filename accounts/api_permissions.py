from rest_framework import permissions


class IsAdminOrIsVehicleOwnerOrIfIsStaffReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the vehicle owner to edit.
    Also allows staff to read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff or obj.customer.user == request.user

        return request.user.is_superuser or obj.customer.user == request.user


class IsStaffOrIsTargetUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the user to edit said user.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff or obj == request.user


class IsAdminOrIsTargetUser(permissions.BasePermission):
    """
    Custom permission to only allow target user to access view
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj == request.user


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin to access view
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class IsStaffOrWriteOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff members to GET list of users
    Anyone can create a user
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff

        return True


class CustomersCanCreateStaffCanRead(permissions.BasePermission):
    """
    Custom permission to only allow customers to create vehicles and
    only staff can read list of vehicles
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff

        try:
            return request.user.is_customer()
        except AttributeError:  # 'AnonymousUser' object has no attribute 'is_customer'
            return False


class StaffCanReadAndHostsCanWrite(permissions.BasePermission):
    """
    Custom permission to only allow staff members to GET list of addresses
    and only hosts can create an address
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff
        elif request.method == 'POST':
            return request.user.is_host()

        return True


class IsHost(permissions.BasePermission):
    """
    Custom permission to only allow Hosts to perform a certain action
    """

    def has_permission(self, request, view):
        return request.user.is_host()
