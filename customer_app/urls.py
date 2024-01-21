from django.urls import path
from customer_app.views import CustomerRegistrationView

urlpatterns = [
    path('customer/register/', CustomerRegistrationView.as_view(), name='customer-registration'),
    
]