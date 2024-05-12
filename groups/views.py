from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from users.permissions import IsInSameOrganization, IsTeacher

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
            case 'create':
                return GroupSerializer
            case 'retrieve' | 'list':
                return GroupSerializer
            case 'add_user':
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
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
        return super().perform_create(serializer)

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
