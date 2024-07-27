"""
URLS for organizations app
"""
from django.urls import path

from .views import *

app_name = 'organizations'

urlpatterns = [
    path('', OrganizationListView.as_view(), name='list_create'),
    path('<int:pk>/', OrganizationRetrieveUpdateView.as_view(), name='detail'),
    path('<int:pk>/add_member/', AddMemberView.as_view(), name='add_member'),
    path('<int:pk>/remove_member/',
         RemoveMemberView.as_view(), name='remove_member'),
]
