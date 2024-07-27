""""
Serializers for the organizations app.
"""

from rest_framework import serializers

from organizations.models import Organization, Membership


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for the organization object"""

    class Meta:
        model = Organization
        fields = ('id', 'name', 'domain')


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for the membership object"""

    class Meta:
        model = Membership
        fields = ('id', 'organization', 'user', 'role')
        read_only_fields = ('organization', 'user')
