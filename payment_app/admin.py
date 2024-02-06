from django.contrib import admin

# Register your models here.
from .models import Subscription,PaymentTransaction

admin.site.register(Subscription)