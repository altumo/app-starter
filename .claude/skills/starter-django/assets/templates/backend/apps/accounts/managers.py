from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    """Custom manager for User model with email as the unique identifier."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        return super().create_superuser(username, email, password, **extra_fields)

    def get_or_create_from_clerk(self, clerk_id, email, **extra_fields):
        """Get or create a user from Clerk authentication data."""
        try:
            user = self.get(clerk_id=clerk_id)
            return user, False
        except self.model.DoesNotExist:
            username = email.split("@")[0]
            # Ensure unique username
            base_username = username
            counter = 1
            while self.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = self.create_user(
                username=username,
                email=email,
                clerk_id=clerk_id,
                **extra_fields,
            )
            return user, True
