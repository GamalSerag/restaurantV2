from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role='customer', **extra_fields):
        print('##################')
        print('role:', role)
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        username = extra_fields.pop('username', None)
        if not username:
            username = email.split('@')[0]  # Using email prefix as username

        user = self.model(email=email, username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        extra_fields.setdefault('username', email)
        return self.create_user(email, password, **extra_fields)



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



# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
    
#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('role', 'superadmin')

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(email, password, **extra_fields)

# class User(AbstractUser):
#     ROLE_CHOICES = (
#         ('superadmin', 'Super Admin'),
#         ('restaurant_owner', 'Restaurant Owner'),
#         ('customer', 'Customer'),
#         ('deliveryman', 'Delivery Man'),
#     )
#     objects = CustomUserManager()
#     email = models.EmailField(unique=True)
#     role = models.CharField(max_length=16, choices=ROLE_CHOICES)
#     REQUIRED_FIELDS = []