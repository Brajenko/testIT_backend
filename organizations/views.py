from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from users.permissions import IsTeacher

from .serializers import *
from .permissions import *

    
class OrganizationView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    
    def get_permissions(self):
        match self.request.method:
            case 'POST':
                return [IsAuthenticated(), IsTeacher(), HasNoOrg()]
            case 'GET':
                return [AllowAny(), ]
            case _:
                return super().get_permissions()

    def perform_create(self, serializer):
        """Sets the current user as the owner of the organization."""
        serializer.save(owner=self.request.user)
        return super().perform_create(serializer)

    def list(self, request, *args, **kwargs):
        """List all organizations new user can join."""
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create new organization. This method not used in the current version."""
        return super().create(request, *args, **kwargs)
