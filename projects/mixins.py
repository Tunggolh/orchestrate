from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from projects.models import Projects, ProjectMembership


class ProjectPermissionMixin:
    def check_permissions_manager(self, project_id, user):
        project = get_object_or_404(Projects, pk=project_id)

        if not self.is_project_manager(project, user):
            return Response({"message": "You don't have a permission to do this action"}, status=status.HTTP_403_FORBIDDEN)

        return None

    def check_permissions_member(self, project_id, user):
        project = get_object_or_404(Projects, pk=project_id)

        if not self.is_project_member(project, user):
            return Response({"message": "You are not a member of this project"}, status=status.HTTP_403_FORBIDDEN)

        return None

    def is_project_member(self, project, user):
        return project.members.filter(user=user).exists()

    def is_project_manager(self, project, user):
        return project.members.filter(user=user, role=ProjectMembership.PROJECT_MANAGER).exists()
