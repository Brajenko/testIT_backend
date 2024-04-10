from django.urls import path, include
from rest_framework import routers
from .views import MyTestsViewSet, TestView, CompletionViewSet


router = routers.SimpleRouter()
router.register(r'tests/created', MyTestsViewSet, basename='Test')
router.register(r'completions', CompletionViewSet, basename='Completion')

urlpatterns = [
    path('', include(router.urls)),
    path('tests/<uuid:public_uuid>/', TestView.as_view())
]