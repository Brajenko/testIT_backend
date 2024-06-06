from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import CompletionViewSet

router = SimpleRouter()
router.register(r'', CompletionViewSet)

urlpatterns = [
    path(r'', include(router.urls), name='completion')
]
