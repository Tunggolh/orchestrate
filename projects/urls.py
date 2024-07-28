"""
URLS for projects app
"""

from django.urls import path

from .views import *

app_name = 'projects'

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='list_create'),
    path('<int:pk>/', ProjectRetrieveUpdateView.as_view(), name='detail'),
    path('<int:pk>/members/', ProjectMembersListView.as_view(), name='members'),
    path('<int:pk>/add_member/', ProjectAddMemberView.as_view(), name='add_member'),
    path('<int:pk>/remove_member/',
         ProjectRemoveMemberView.as_view(), name='remove_member'),
]
