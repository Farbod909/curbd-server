from rest_framework import permissions


class IsAdminOrIsSpaceOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins or the space owner to edit.
    Also allows staff to read.
    """
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.host.user == request.user


class HostsCanCreateStaffCanRead(permissions.BasePermission):
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
