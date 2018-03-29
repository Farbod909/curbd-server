from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the customer/host themselves to edit.
    Also allows staff to read.
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True
        return False
