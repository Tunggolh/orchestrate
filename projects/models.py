from django.db import models
from django.contrib.auth import get_user_model

from core.models import BaseModel
from organizations.models import Organization


class Projects(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    PROJECT_MANAGER = 'manager'
    PROJECT_MEMBER = 'member'

    ROLE_CHOICES = [
        (PROJECT_MANAGER, 'Project Manager'),
        (PROJECT_MEMBER, 'Project Member'),
    ]

    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=PROJECT_MEMBER)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f'{self.project} - {self.user} : {self.role}'
