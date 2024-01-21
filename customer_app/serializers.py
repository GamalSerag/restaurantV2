from rest_framework import serializers
from customer_app.models import Customer
from auth_app.serializers import UserSerializer

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = '__all__'