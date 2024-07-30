"""
Serializers for the tasks app
"""

from rest_framework import serializers

from tasks.models import Columns, Tasks


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Columns
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = '__all__'


class TaskListSerializer(serializers.ModelSerializer):
    assignee_name: dict = serializers.ReadOnlyField(
        source='assignee.full_name')

    class Meta:
        model = Tasks
        fields = '__all__'
