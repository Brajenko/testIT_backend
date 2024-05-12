from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework import views

from .serializers import *
from .permissions import *

User = get_user_model()


class UserView(generics.ListCreateAPIView):
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
        return User.objects.filter(organization=self.request.user.organization) # type: ignore


class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
