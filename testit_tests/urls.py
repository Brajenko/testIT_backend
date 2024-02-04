from django.urls import path, include
from rest_framework import routers
from .views import TestViewSet, CompletionViewSet


router = routers.SimpleRouter()
router.register(r'test', TestViewSet)
router.register(r'completion', CompletionViewSet)

urlpatterns = [
    path('', include(router.urls))
]