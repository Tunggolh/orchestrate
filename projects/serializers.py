"""
Serializers for the projects app.
"""

from rest_framework import serializers

from projects.models import Projects


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'


class ProjectMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'
