from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    """Allows access only to teachers"""

    def has_permission(self, request, view):   # type: ignore
        if not request.user.is_authenticated:
            return False
        return request.user.is_teacher


class IsInSameOrganization(BasePermission):
    """Allows access only if organizations of user and objects is same"""

    def has_object_permission(self, request, view, obj):   # type: ignore
        if not request.user.is_authenticated:
            return False
        return request.user.organization == obj.organization
