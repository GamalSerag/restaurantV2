from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

from admin_app.models import Admin
from customer_app.models import Customer

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # Assuming role is already correctly set in the session in your view
        role = request.session.pop('temp_role', 'customer')  # default role if none specified

        user = super().save_user(request, sociallogin, form=form)
        user.role = role
        user.save()

        # Depending on the role, create the appropriate profile
        if user.role == 'customer':
            Customer.objects.create(user=user)
        elif user.role == 'restaurant_owner':
            Admin.objects.create(user=user)

        return user
    
    def __init__(self):
        pass