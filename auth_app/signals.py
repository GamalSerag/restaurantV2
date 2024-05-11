from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from customer_app.models import Customer


@receiver(user_signed_up)
def create_customer_profile(sender, user, **kwargs):
    if user.role == 'customer':
        # Check if the user already has a customer profile
        if not hasattr(user, 'customer_profile'):
            # Create a new customer profile
            customer_data = {
                'user': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                
            }
            Customer.objects.create(**customer_data)