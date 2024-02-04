from django.shortcuts import render
from rest_framework import viewsets
from .models import Test, Completion
from .serializers import TestSerializer, CompletionSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class CompletionViewSet(viewsets.ModelViewSet):
    queryset = Completion.objects.all()
    serializer_class = CompletionSerializer
    
    def create(self, request):
        request.data["score"] = 0
        return super().create(request)
    
    def update(self, request):
        request.data["score"] = 0
        return super().update(request)
    
    def partial_update(self, request):
        request.data["score"] = 0
        return super().partial_update(request)
    
    def get_queryset(self):
        student = self.request.GET.get("student")
        if student:
            return Completion.objects.filter(student=student)
        return Completion.objects.all()

