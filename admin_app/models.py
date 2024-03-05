from django.db import models
from auth_app.models import User
from payment_app.models import Subscription
from restaurant_app.models import Restaurant
# from django.contrib.auth.models import AbstractUser

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank= True)
    is_subscribed = models.BooleanField(default=False)

    def __str__(self):
        return f"Admin #{self.pk} - {self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if self.subscription:
            self.is_subscribed = True
        else:
            self.is_subscribed = False
        super().save(*args, **kwargs)   