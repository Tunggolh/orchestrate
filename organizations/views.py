"""
This file contains the views for the organizations app.
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from organizations.serializers import OrganizationSerializer
from organizations.models import Organization, Membership


class OrganizationListView(generics.ListAPIView):
    """
    List organizations of the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(memberships__user=self.request.user)


class OrganizationCreateView(generics.CreateAPIView):
    """
    Create a new organization.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        organization = serializer.save()

        Membership.objects.create(
            organization=organization,
            user=self.request.user,
            role=Membership.OWNER
        )
