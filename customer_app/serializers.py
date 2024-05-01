from rest_framework import serializers
from customer_app.models import Customer
from auth_app.serializers import UserSerializer
from restaurant_app.models import Restaurant
from review_app.models import TotalRating

class CustomerSerializer(serializers.ModelSerializer):
    # user = UserSerializer()

    class Meta:
        model = Customer
        
        exclude = ['user', 'latitude', 'longitude', 'is_active_phone', 'favorites']


class FavoriteRestaurantSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    restaurant_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'logo', 'background', 'country', 'city', 'restaurant_rate']

    def get_restaurant_rate(self, obj):
        try:
            total_rating = TotalRating.objects.get(restaurant=obj)
            return total_rating.total_rating
        except TotalRating.DoesNotExist:
            return None
        
    def get_city(self, obj):
        return obj.city.name if obj.city else None

    def get_country(self, obj):
        return obj.city.country.name if obj.city else None