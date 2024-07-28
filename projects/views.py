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

    def get_queryset(self):
        return Projects.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save()

        ProjectMembership.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMembership.PROJECT_MANAGER
        )

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
