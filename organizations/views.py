from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

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
