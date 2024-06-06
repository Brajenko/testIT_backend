from rest_framework.permissions import BasePermission

class CanPassTest(BasePermission):
    def has_object_permission(self, request, view, obj): # type: ignore
        if not request.user.is_authenticated:
            return False
        if request.user.is_teacher:
            return False
        user_groups = request.user.groups.all()
        obj_groups = obj.available_for.all()
        for ug in user_groups:
            if ug in obj_groups:
                return True
        return False
    
class IsTestCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.creator == request.user