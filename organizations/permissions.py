from rest_framework.permissions import BasePermission

class HasNoOrg(BasePermission):
    def has_permission(self, request, view): # type: ignore
        return not getattr(request.user, 'organization', None)
