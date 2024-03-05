from rest_framework import serializers
from admin_app.models import Admin
from auth_app.serializers import UserSerializer
from restaurant_app.models import Restaurant

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    restaurant_name = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = Admin
        fields = ['id', 'user', 'phone_number', 'created_at', 'first_name', 'last_name', 'restaurant', 'restaurant_name', 'subscription', 'is_subscribed']

    def get_restaurant_name(self, obj):
        if obj.restaurant:
            return obj.restaurant.name
        return None
    
    def get_subscription(self, obj):
        if obj.restaurant:
            return {'id': obj.subscription.id, 'name': obj.subscription.name, 'price': obj.subscription.price, 'commission_rate':obj.subscription.commission_rate, 'duration': obj.subscription.duration }
        return None