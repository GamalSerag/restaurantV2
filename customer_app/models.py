from django.db import models
from django.contrib.auth.models import AbstractUser

from auth_app.models import User
from restaurant_app.models import Restaurant

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    # provider_id = models.CharField(max_length=255, null=True, blank=True)
    # provider = models.CharField(max_length=255, null=True, blank=True)
    is_active_phone = models.BooleanField(default=False)
    favorites = models.ManyToManyField(Restaurant, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    

    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
