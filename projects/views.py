"""
This file contains the views for the projects app.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from organizations.mixins import OrganizationPermissionMixin
from organizations.models import Membership
from projects.mixins import ProjectPermissionMixin
from projects.serializers import ProjectMembersSerializer, ProjectSerializer, ProjectMembershipSerializer
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

    def perform_create(self, serializer):
        project = serializer.save()

        ProjectMembership.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMembership.PROJECT_MANAGER
        )

    def create(self, request, *args, **kwargs):

        data = request.data
        organization_pk = kwargs.get('organization_pk', None)

        if organization_pk:
            data = {
                'organization': organization_pk,
                'name': data.get('name', None),
                'description': data.get('description', None)
            }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        organization_id = serializer.validated_data.get('organization', None)

        organization_member = Membership.objects.filter(
            organization=organization_id, user=request.user).filter(
                Q(role=Membership.ROLE_OWNER) | Q(role=Membership.ROLE_MANAGER)
        ).exists()

        if not organization_member:
            return Response(
                {'error': 'You are not a member of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectRetrieveUpdateView(generics.RetrieveUpdateAPIView, ProjectPermissionMixin):
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

        permission_error = self.check_permissions_member(
            project.id, request.user)

        if permission_error:
            return permission_error

        serializer = self.get_serializer(project)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        project = self.get_object()

        permission_error = self.check_permissions_manager(
            project.id, request.user)

        if permission_error:
            return permission_error

        serializer = self.get_serializer(
            project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ProjectMembersListView(generics.ListAPIView, ProjectPermissionMixin):
    """
    List all members of a project.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectMembersSerializer

    def list(self, request, *args, **kwargs):
        project = get_object_or_404(Projects, id=kwargs['pk'])

        permission_error = self.check_permissions_member(
            project.id, request.user)

        if permission_error:
            return permission_error

        queryset = ProjectMembership.objects.filter(project=project)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProjectAddMemberView(generics.CreateAPIView, ProjectPermissionMixin, OrganizationPermissionMixin):
    """
    Add a member to a project.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectMembershipSerializer

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Projects, id=kwargs['pk'])

        permission_error = self.check_permissions_manager(
            project.id, request.user)

        if permission_error:
            return permission_error

        user_id = request.data.get('user', None)

        data = {
            'project': project.id,
            'user': user_id,
            'role': request.data.get('role', ProjectMembership.PROJECT_MEMBER)
        }

        is_organization_member = self.is_organization_member(
            project.organization, user_id)

        if not is_organization_member:
            return Response(
                {'error': 'User is not a member of the organization.'},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectRemoveMemberView(generics.DestroyAPIView, ProjectPermissionMixin):
    """
    Remove a member from a project.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectMembershipSerializer

    def delete(self, request, *args, **kwargs):
        user_id = request.data.get('user', None)

        if not user_id:
            return Response(
                {'error': 'User is required.'},
                status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Projects, id=kwargs['pk'])

        permission_error = self.check_permissions_manager(
            project.id, request.user)

        if permission_error:
            return permission_error

        return self.destroy(request, user_id, project)

    def destroy(self, request, user_id, project):

        is_current_user = int(user_id) == request.user.id

        if is_current_user and ProjectMembership.objects.filter(project=project).count() == 1:
            return Response(
                {'error': "Cannot remove yourself from the project. You're the only member."},
                status=status.HTTP_400_BAD_REQUEST)

        membership = ProjectMembership.objects.filter(
            project=project, user=user_id).first()

        if not membership:
            return Response(
                {'error': 'User is not a member of the project.'},
                status=status.HTTP_400_BAD_REQUEST)

        if not is_current_user and membership.role == ProjectMembership.PROJECT_MANAGER:
            return Response(
                {'error': 'Cannot remove a manager from the project.'},
                status=status.HTTP_400_BAD_REQUEST)

        membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
