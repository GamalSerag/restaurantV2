from django.db import models
from auth_app.models import User
from payment_app.models import Subscription
from restaurant_app.models import Restaurant
from django.db.models.signals import post_save
from django.dispatch import receiver


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank= True)
    is_subscribed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    has_submitted_docs = models.BooleanField(default=False)

    def __str__(self):
        return f"Admin #{self.pk} - {self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if self.subscription:
            self.is_subscribed = True
        else:
            self.is_subscribed = False
        super().save(*args, **kwargs)   
    
    @receiver(post_save, sender='admin_app.AdminDoc')
    def update_admin_docs_status(sender, instance, created, **kwargs):
        if created:
            instance.admin.has_submitted_docs = True
            instance.admin.save()


def admin_docs_image_path(instance, filename):
    # Get the admin's legal name and concatenate it with the filename
    admin_name = instance.leagal_name.replace(" ", "_")
    # Use the admin's legal name as the folder name
    return f'admin_docs/{admin_name}/{filename}'
    

class AdminAdress(models.Model):
    line1 = models.CharField()
    postal_code = models.CharField()
    city = models.CharField()



class AdminDoc(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin_docs')
    leagal_name = models.CharField()
    phone = models.CharField(blank=True, null=True)
    ID_photo = models.FileField(upload_to =admin_docs_image_path)
    business_register = models.FileField(upload_to =admin_docs_image_path)
    address = models.ForeignKey(AdminAdress, on_delete=models.CASCADE)
    superadmin_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.leagal_name} -  {self.admin.user.email}"