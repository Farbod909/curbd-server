from rest_framework import permissions


class IsAdminOrIsStaff(permissions.BasePermission):
    """
    Custom permission to only allow staff to browse.
    """
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff


class ReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the customer/host themselves to edit.
    Also allows staff to read.
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True
        return False
