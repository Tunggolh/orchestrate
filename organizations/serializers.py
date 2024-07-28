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


class MembersSerializer(serializers.ModelSerializer):
    """Serializer for organization members"""
    member_name: str = serializers.ReadOnlyField(source='user.full_name')
    member_id: int = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Membership
        fields = ['member_id', 'member_name', 'role']


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for the membership object"""

    class Meta:
        model = Membership
        fields = ('id', 'organization', 'user', 'role')
