"""
This file contains the views for the tasks of a project.
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from projects.models import Project, ProjectMembership

from organizations.models import Organization

from tasks.models import Columns
from tasks.serializer import ColumnSerializer


class ColumnListCreateView(generics.ListCreateAPIView):
    """
    List all columns in a project or create a new column.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ColumnSerializer

    def is_user_a_project_member(self, project_id, user):
        project = get_object_or_404(Project, pk=project_id)
        return project.members.filter(user=user).exists()

    def is_user_a_project_manager(self, project_id, user):
        project = get_object_or_404(Project, pk=project_id)
        return project.members.filter(user=user, role=ProjectMembership.PROJECT_MANAGER).exists()

    def get(self, request, *args, **kwargs):
        project_id = request.GET.get('project_id', None)

        if not project_id:
            return Response(
                {"message": "query params project_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not self.is_user_a_project_member(project_id, request.user):
            return Response(
                {"message": "You are not a member of this project"},
                status=status.HTTP_403_FORBIDDEN
            )

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

    def post(self, request, *args, **kwargs):
        data = request.data

        user = request.user

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data.get('project', None)

        if not self.is_user_a_project_member(
                project_id, user):
            return Response(
                {"message": "You are not a member of this project"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not self.is_user_a_project_member(project_id, user):
            return Response(
                {"message": "You are not a member of this project"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not self.is_user_a_project_manager(project_id, user):
            return Response(
                {"message": "You are not a project manager"},
                status=status.HTTP_403_FORBIDDEN
            )

        data['project'] = project_id

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
