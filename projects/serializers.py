"""
Serializers for the projects app.
"""

from rest_framework import serializers

from projects.models import Projects, ProjectMembership


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'


class ProjectMembersSerializer(serializers.ModelSerializer):
    member_id = serializers.ReadOnlyField(source='user.id')
    member_name = serializers.ReadOnlyField(source='user.full_name')

    class Meta:
        model = ProjectMembership
        fields = ['member_id', 'member_name', 'role']


class ProjectMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = '__all__'
