from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    """Custom user model that uses email as the unique identifier."""

    email = models.EmailField(unique=True)
    clerk_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Clerk user ID (e.g. user_2abc123...)",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
