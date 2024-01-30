from django.urls import path, include
from rest_framework import routers
from .views import TestViewSet


router = routers.SimpleRouter()
router.register(r'test', TestViewSet)

urlpatterns = [
    path('', include(router.urls))
]