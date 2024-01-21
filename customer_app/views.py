from rest_framework import generics
from customer_app.models import Customer
from customer_app.serializers import CustomerSerializer

class CustomerRegistrationView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer