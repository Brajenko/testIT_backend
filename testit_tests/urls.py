from django.urls import path, include
from rest_framework_nested import routers
from .views import *


created_tests_router = routers.SimpleRouter()
created_tests_router.register(r'tests/created', MyTestsViewSet, basename='Test')

tests_router = routers.SimpleRouter()
tests_router.register(r'tests', TestViewSet, basename='Public Test')

test_completions_router = routers.NestedSimpleRouter(tests_router, r'tests', lookup='test')
test_completions_router.register(
    r'completions', MyTestCompletionsViewSet, basename='Test complitions'
)

urlpatterns = [
    path('', include(created_tests_router.urls)),
    path('', include(tests_router.urls)),
    path('', include(test_completions_router.urls)),
    # path('tests/<uuid:public_uuid>/', TestView.as_view()),
]
