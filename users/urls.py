from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

me = views.CurrentUserViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
    }
)

my_completions = views.CurrentUserViewSet.as_view(
    {
        'get': 'get_completions'
    }
)

router = DefaultRouter()
router.register(r'', views.UserViewSet, basename='users')

urlpatterns = [
    path('token/obtain/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('me', me),
    path('me/completions/', my_completions)    
]
