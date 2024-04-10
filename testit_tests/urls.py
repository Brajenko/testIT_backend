from django.urls import path, include
from rest_framework_nested import routers
from .views import *


router = routers.SimpleRouter()
router.register(r'tests/created', MyTestsViewSet, basename='Test')

nested_router = routers.NestedSimpleRouter(router, r'')
router.register(r'tests/<uuid:public_uuid>/completions', MyTestCompletionsViewSet, basename='Test complitions')

urlpatterns = [
    path('', include(router.urls)),
    path('tests/<uuid:public_uuid>/', TestView.as_view()),

]