from rest_framework import permissions


class IsStaffMember(permissions.BasePermission):
    """
    Custom permission to only allow staff members to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff_member)
