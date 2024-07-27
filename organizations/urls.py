"""
URLS for organizations app
"""
from django.urls import path

from .views import *

app_name = 'organizations'

urlpatterns = [
    path('', OrganizationListView.as_view(), name='list'),
    path('', OrganizationCreateView.as_view(), name='create'),
    path('add_member/', AddMemberView.as_view(), name='add_member'),
    path('remove_member/', RemoveMemberView.as_view(), name='remove_member'),
]
