from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularJSONAPIView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/students/', include('testit_api.student_urls')),
    # path('api/teachers/', include('testit_api.teacher_urls')),
    path('api/tests/', include('questions.urls')),
    path('api/users/', include('users.urls')),
    path('api/organizations/', include('organizations.urls')),
    path('api/completions/', include('completions.urls')),
    path('api/groups/', include('groups.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/json/', SpectacularJSONAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/schema/redoc',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    )
]
