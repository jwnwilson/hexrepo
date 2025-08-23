from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import BaseModel


class User(AbstractUser, BaseModel):
    """Custom user model with verification status."""

    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this user has verified their email address.",
    )

    # Override the default id field from AbstractUser to use UUID
    # The BaseModel already provides this, so we don't need to redefine it

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username
