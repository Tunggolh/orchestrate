from django.db import models
from core.models import BaseModel


class Organization(BaseModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True, db_index=True)
