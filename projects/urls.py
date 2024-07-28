"""
URLS for projects app
"""

from django.urls import path

from .views import *

app_name = 'projects'

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='list_create'),
    # path('<int:pk>/', ProjectRetrieveUpdateView.as_view(), name='detail'),
    # path('<int:pk>/add_member/', AddMemberView.as_view(), name='add_member'),
    # path('<int:pk>/remove_member/',
    #      RemoveMemberView.as_view(), name='remove_member'),
]
