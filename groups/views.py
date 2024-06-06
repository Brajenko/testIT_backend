from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema

from users.permissions import IsTeacher

from .serializers import *


class GroupViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Group.objects.all()

    def get_serializer_class(self): # type: ignore
        match self.action:
            case 'list':
                return GroupSerializer
            case 'create' | 'retrieve' | 'destroy':
                return GroupSerializer
            case 'add_user' | 'remove_user':
                return GroupAddUserSerializer
            case _:
                return GroupSerializer
            
    def get_queryset(self): # type: ignore
        return Group.objects.filter(groupinfo__organization=self.request.user.organization) # type: ignore because user is 100% authenficated
    
    def get_permissions(self):
        match self.action:
            case 'create':
                return [IsAuthenticated(), IsTeacher()]
            case 'retrieve' | 'list':
                return [IsAuthenticated()]
            case 'add_user':
                return [IsTeacher()]
            case _:
                return super().get_permissions()
            
    @extend_schema(responses=GroupSerializer)
    def list(self, request: Request, *args, **kwargs):
        """List all groups in organization"""
        return super().list(request, *args, **kwargs)
            
    @extend_schema(request=GroupSerializer, responses=GroupSerializer)
    def save(self, request: Request, *args, **kwargs):
        """Creates group."""
        return super().create(request, *args, **kwargs)
    
    @extend_schema(responses=GroupSerializer)
    def retrieve(self, request: Request, *args, **kwargs):
        """Returns group."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(responses=GroupSerializer)
    def destroy(self, request: Request, *args, **kwargs):
        """Deletes group."""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(request=GroupAddUserSerializer, responses=GroupSerializer)
    @action(detail=True, methods=['POST'])
    def add_user(self, request: Request, *args, **kwargs):
        """Adds user to group."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        instance = self.get_object()
        if user.organization != instance.groupinfo.organization:
            raise ValidationError('User and group must refer to the same organization')
        instance.user_set.add(user)
        return Response(GroupSerializer(instance).data)
    
    @extend_schema(request=GroupAddUserSerializer, responses=GroupSerializer)
    @action(detail=True, methods=['POST'])
    def remove_user(self, request: Request, *args, **kwargs):
        """Removes user from group."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        instance = self.get_object()
        instance.user_set.remove(user)
        return Response(GroupSerializer(instance).data)
