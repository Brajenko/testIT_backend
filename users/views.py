from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework import generics

from .serializers import RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
