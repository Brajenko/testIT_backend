from django.urls import path

from .views import *

urlpatterns = [
    path('', OrganizationView.as_view(), name='list_and_create_organization'),
]
