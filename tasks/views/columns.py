"""
This file contains the views for the columns of the projects.
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from projects.mixins import ProjectPermissionMixin
from projects.models import Project, ProjectMembership

from organizations.models import Organization

from tasks.models import Columns
from tasks.serializer import ColumnSerializer


class ColumnListCreateView(generics.ListCreateAPIView, ProjectPermissionMixin):
    """
    List all columns in a project or create a new column.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ColumnSerializer

    def get(self, request, *args, **kwargs):
        project_id = request.GET.get('project_id', None)

        if not project_id:
            return Response(
                {"message": "query params project_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        permission_error = self.check_permissions_member(
            project_id, request.user)

        if permission_error:
            return permission_error

        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        project_id = request.GET.get('project_id')
        queryset = Columns.objects.filter(project=project_id)

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
        permission_error = self.check_permissions_manager(
            project_id, request.user)

        if permission_error:
            return permission_error

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
