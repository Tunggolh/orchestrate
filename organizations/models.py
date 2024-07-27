from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_MANAGER = 'manager'
    ROLE_MEMBER = 'member'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_MEMBER, 'Member'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=255, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user} in {self.organization}"
