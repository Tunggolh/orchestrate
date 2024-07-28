"""
Serializers for the projects app.
"""

from rest_framework import serializers

from projects.models import Projects, ProjectMembership


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'


class ProjectMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = '__all__'
