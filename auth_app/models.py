from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('restaurant_owner', 'Restaurant Owner'),
        ('customer', 'Customer'),
        ('deliveryman', 'Delivery Man'),
    )
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    REQUIRED_FIELDS = []
