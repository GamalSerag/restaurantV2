from django.urls import path
from customer_app.views import CustomerViewSet

urlpatterns = [
    path('customers/', CustomerViewSet.as_view({'get': 'list'}), name='customer-registration'),
    
]