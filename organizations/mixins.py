from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from organizations.models import Organization, Membership


class OrganizationPermissionMixin:
    def check_permissions_owner(self, organization_id, user):
        organization = get_object_or_404(Organization, pk=organization_id)

        if not self.is_organization_owner(organization, user):
            return Response({"message": "You don't have a permission to do this action"}, status=status.HTTP_403_FORBIDDEN)

        return None

    def check_permissions_member(self, organization_id, user):
        organization = get_object_or_404(Organization, pk=organization_id)

        if not self.is_organization_member(organization, user):
            return Response({"message": "You are not a member of this organization"}, status=status.HTTP_403_FORBIDDEN)

        return None

    def is_organization_member(self, organization, user):
        return organization.memberships.filter(user=user).exists()

    def is_organization_owner(self, organization, user):
        return organization.memberships.filter(user=user, role=Membership.ORGANIZATION_OWNER).exists()
