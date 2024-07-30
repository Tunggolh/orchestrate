"""
URLs for the tasks app.
"""

from django.urls import path

from .views import *

app_name = 'tasks'

urlpatterns = [
    path('columns/', ColumnListCreateView.as_view(), name='columns_list_create'),
    path('columns/<int:pk>/', ColumnRetrieveUpdateDestroyView.as_view(),
         name='column_detail'),
    path('tasks/', TaskListCreateView.as_view(), name='tasks_list_create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(),
         name='task_detail'),
]
