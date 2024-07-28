"""
This file contains the views for the projects app.
"""

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from projects.serializers import ProjectSerializer, ProjectMembershipSerializer
from projects.models import Projects, ProjectMembership


class ProjectListView(generics.ListCreateAPIView):
    """
    List all projects the user is a member of or create a new project.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Projects.objects.filter(memberships__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save()

        ProjectMembership.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMembership.ROLE_OWNER
        )
