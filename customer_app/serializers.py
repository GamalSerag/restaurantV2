from rest_framework import serializers
from customer_app.models import Customer
from auth_app.serializers import UserSerializer
from restaurant_app.models import Restaurant

class CustomerSerializer(serializers.ModelSerializer):
    # user = UserSerializer()

    class Meta:
        model = Customer
        
        exclude = ['user', 'latitude', 'longitude', 'is_active_phone', 'favorites']


class FavoriteRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'logo', 'background']