from rest_framework import viewsets
from .models import Test, Completion
from .serializers import TestSerializer, CompletionSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions


class IsTestCreator(permissions.BasePermission):
    """
    Permission checks if user created test obj
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        return request.user == obj.creator


class CanPassTest(permissions.BasePermission):
    """
    Permission checks if user can pass this test
    """
    def has_object_permission(self, request, view, obj):
        print(request.user)
        print(obj)
        return True


class TestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTestCreator | CanPassTest]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    
    def create(self, request):
        request.data["creator"] = request.user.id
        return super().create(request)


class CompletionViewSet(viewsets.ModelViewSet):
    queryset = Completion.objects.all()
    serializer_class = CompletionSerializer
    
    def create(self, request):
        request.data["score"] = 0
        request.data["student"] = request.user.id
        return super().create(request)
    
    def update(self, request):
        user = self.request.user
        compl_id = request.data["id"]
        compl: Completion = Completion.objects.get(id=compl_id)
        if user != compl.test.creator:
            raise PermissionDenied("You need to be test creator to modify answers.")
        request.data["score"] = 0
        return super().update(request)
    
    def partial_update(self, request):
        request.data["score"] = 0
        return super().partial_update(request)
    
    def get_queryset(self):
        student = self.request.user
        return Completion.objects.filter(student=student)
