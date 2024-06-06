from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import TestViewSet, PublicTestViewSet

tests_router = SimpleRouter()
tests_router.register(r'', TestViewSet, basename='tests')
tests_router.register(r'p', PublicTestViewSet, basename='public_tests')

urlpatterns = [
    path('', include(tests_router.urls)),
]
