"""
This file contains the views for the organizations app.
"""

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from organizations.serializers import MembersSerializer, MembershipSerializer, OrganizationSerializer
from organizations.models import Organization, Membership


class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    List all organizations the user is a member of or create a new organization.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        organization = serializer.save()

        Membership.objects.create(
            organization=organization,
            user=self.request.user,
            role=Membership.ROLE_OWNER
        )


class OrganizationRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update an organization.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer

    def get_object(self):
        pk = self.kwargs['pk']
        return get_object_or_404(Organization, id=pk)

    def retrieve(self, request, *args, **kwargs):
        organization = self.get_object()

        is_member = Membership.objects.filter(
            organization=organization, user=request.user).exists()

        if not is_member:
            return Response(
                {'error': 'You are not a member of this organization.'},
                status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(organization)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        organization = self.get_object()
        organization_owner = Membership.objects.get(
            organization=organization, role=Membership.ROLE_OWNER)

        if organization_owner.user != request.user:
            return Response(
                {'error': 'You are not the owner of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return self.partial_update(request, *args, **kwargs)


class MembersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MembersSerializer

    def list(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, id=kwargs['pk'])

        is_member = Membership.objects.filter(
            organization=organization, user=request.user).exists()

        if not is_member:
            return Response(
                {'error': 'You are not a member of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = Membership.objects.filter(organization=organization)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AddMemberView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MembershipSerializer

    def create(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, id=kwargs['pk'])
        organization_owner = Membership.objects.get(
            organization=organization, role=Membership.ROLE_OWNER)

        if organization_owner.user != request.user:
            return Response(
                {'error': 'You are not the owner of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = {
            'organization': organization.id,
            'user': request.data.get('user'),
            'role': request.data.get('role', Membership.ROLE_MEMBER)
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RemoveMemberView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MembershipSerializer

    def destroy(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, id=kwargs['pk'])
        organization_owner = Membership.objects.get(
            organization=organization, role=Membership.ROLE_OWNER)

        if organization_owner.user != request.user:
            return Response(
                {'error': 'You are not the owner of this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        membership = get_object_or_404(
            Membership, user=request.data.get('user'), organization=organization)

        self.perform_destroy(membership)

        return Response(status=status.HTTP_204_NO_CONTENT)
