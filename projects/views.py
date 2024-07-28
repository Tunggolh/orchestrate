"""
This file contains the views for the projects app.
"""

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from organizations.models import Membership
from projects.serializers import ProjectSerializer, ProjectMembershipSerializer
from projects.models import Projects, ProjectMembership


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects the user is a member of or create a new project.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def list(self, request, *args, **kwargs):

        organization_id = kwargs.get('organization_pk', None)

        if organization_id:
            queryset = Projects.objects.filter(organization=organization_id)
        else:
            queryset = Projects.objects.filter(
                members__user=request.user)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization_id = serializer.validated_data.get('organization', None)

        organization_member = Membership.objects.filter(
            organization=organization_id, user=request.user).exists()

        if not organization_member:
            return Response(
                {'error': 'You are not a member of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a project.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_object(self):
        pk = self.kwargs['pk']
        return get_object_or_404(Projects, id=pk)

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()

        is_member = ProjectMembership.objects.filter(
            project=project, user=request.user).exists()

        if not is_member:
            return Response(
                {'error': 'You are not a member of this project.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(project)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        project = self.get_object()

        is_member = ProjectMembership.objects.filter(
            project=project, user=request.user).exists()

        if not is_member:
            return Response(
                {'error': 'You are not a member of this project.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(
            project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
