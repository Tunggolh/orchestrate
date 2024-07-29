from django.db import models
from django.contrib.auth import get_user_model

from core.models import BaseModel

from projects.models import Projects


class Columns(models.Model):
    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=50)
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('project', 'name')
        ordering = ['position']

    def __str__(self):
        return self.name


class Task(BaseModel):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    due_date = models.DateTimeField()

    columns = models.ForeignKey(
        Columns, on_delete=models.CASCADE, related_name='tasks')

    project = models.ForeignKey(
        Projects, on_delete=models.CASCADE, related_name='tasks')

    assignee = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title
