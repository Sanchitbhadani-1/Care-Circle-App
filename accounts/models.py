from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    # Configuring how to make users without using a username, but with only an email

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Our custom user: logs in with an email address instead of a username."""

    username = None  # we don't use usernames at all
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"  # the field people log in with
    REQUIRED_FIELDS = []  # extra fields asked for when creating an admin (none for now)

    objects = UserManager()

    def __str__(self):
        return self.email
