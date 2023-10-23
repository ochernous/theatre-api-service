from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow to read for any user and all methods for staff users.
    """
    def has_permission(self, request, view):
        return bool((request.method in SAFE_METHODS and request.user) or (request.user and request.user.is_staff))
