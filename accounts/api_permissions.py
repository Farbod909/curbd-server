from rest_framework import permissions


class IsAdminOrIsOwnerOrIsStaffReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the owner to edit.
    Also allows staff to read.
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff or obj.customer.user == request.user

        return request.user.is_superuser or obj.customer.user == request.user


class IsStaff(permissions.BasePermission):
    """
    Custom permission to only allow staff to browse.
    """
    def has_permission(self, request, view):
        return request.user.is_staff


class IsStaffOrIsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the user to edit said user.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        # Always allow GET, HEAD or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff or obj == request.user
