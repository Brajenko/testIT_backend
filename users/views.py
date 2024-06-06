from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from completions.serializers import CompletionCreationSerializer

from .serializers import *
from .permissions import *

User = get_user_model()

class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = UserSerializer

    def get_permissions(self):
        match self.request.method:
            case 'GET':
                return [IsAuthenticated(), ]
            case 'POST':
                return [AllowAny(), ]
            case _:
                return [IsAuthenticated(), ]
            
    def get_queryset(self): # type: ignore
        if self.request.user.is_anonymous:
            return User.objects.none()
        return User.objects.filter(organization=self.request.user.organization) # type: ignore
    
    def create(self, request, *args, **kwargs):
        """Create new user. (register)"""
        return super().create(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        """List all users"""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Return user"""
        return super().retrieve(request, *args, **kwargs)

class CurrentUserViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(responses=CompletionCreationSerializer(many=True))
    @action(methods=['get'], detail=True, url_name='get_completions')
    def get_completions(self, request, obj=None):
        """Get all completions of current user. (students only!)"""
        completions = self.get_object().completion_set.all() # type: ignore
        serializer = CompletionCreationSerializer(completions, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Get info about current user."""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update current user."""
        return super().update(request, *args, **kwargs)
