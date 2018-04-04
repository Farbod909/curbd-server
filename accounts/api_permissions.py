from rest_framework import permissions


class IsAdminOrIsCarOwnerOrIfIsStaffReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the car owner to edit.
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
        # Read permissions are allowed to any request
        # Always allow GET, HEAD or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff or obj == request.user


class IsAdminOrIsTargetUser(permissions.BasePermission):
    """
    Custom permission to only allow target user to access view
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj == request.user
