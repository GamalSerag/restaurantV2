from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USERNAME_FIELD = 'email'
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('restaurant_owner', 'Restaurant Owner'),
        ('customer', 'Customer'),
        ('deliveryman', 'Delivery Man'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    REQUIRED_FIELDS = []