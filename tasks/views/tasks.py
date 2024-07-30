"""
This file contains the views for the tasks of a project.
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from projects.mixins import ProjectPermissionMixin

from tasks.models import Tasks
from tasks.serializer import TaskSerializer, TaskListSerializer


class TaskListCreateView(generics.ListCreateAPIView, ProjectPermissionMixin):
    """
    List all tasks in a project or create a new task.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskListSerializer

        return TaskSerializer

    def get(self, request, *args, **kwargs):
        project_id = request.GET.get('project_id', None)
        column_id = request.GET.get('column_id', None)

        if not column_id or not project_id:
            return Response(
                {"message": "query params project_id or column_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        permission_error = self.check_permissions_member(
            project_id, request.user)

        if permission_error:
            return permission_error

        return self.list(request, project_id, column_id)

    def list(self, request, project_id, column_id):

        filters = {}

        if project_id:
            filters['project_id'] = project_id

        if column_id:
            filters['column_id'] = column_id

        queryset = Tasks.objects.filter(**filters)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data.get('project', None)
        permission_error = self.check_permissions_member(
            project_id, request.user)

        if permission_error:
            return permission_error

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView, ProjectPermissionMixin):
    """
    Retrieve, update or delete a task.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_object(self):
        task_id = self.kwargs.get('pk')
        return get_object_or_404(Tasks, pk=task_id)

    def get(self, request, *args, **kwargs):
        project_id = request.GET.get('project_id', None)
        column_id = request.GET.get('column_id', None)

        if not column_id or not project_id:
            return Response(
                {"message": "query params project_id or column_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        permission_error = self.check_permissions_member(
            project_id, request.user)

        if permission_error:
            return permission_error

        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(
            task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        permission_error = self.check_permissions_member(
            task.project.id, request.user)

        if permission_error:
            return permission_error

        self.perform_update(serializer)

        if getattr(task, '_prefetched_objects_cache', None):
            task._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()

        permission_error = self.check_permissions_member(
            task.project.id, request.user)

        if permission_error:
            return permission_error

        self.perform_destroy(task)
        return Response(status=status.HTTP_204_NO_CONTENT)
