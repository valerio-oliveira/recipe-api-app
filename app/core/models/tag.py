"""
Tag model.
"""
from django.conf import settings
from .user_manager import UserManager
from django.db import models
from django.contrib.auth.models import (
    PermissionsMixin,
)

class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
