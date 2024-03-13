from rest_framework import serializers
from .models import Admin, AdminAdress, AdminDoc
from auth_app.serializers import UserSerializer
from restaurant_app.models import Restaurant
from drf_writable_nested.serializers import WritableNestedModelSerializer

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    restaurant_name = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = Admin
        fields = ['id', 'user', 'phone_number', 'created_at', 'first_name', 'last_name', 'restaurant', 'restaurant_name', 'subscription', 'is_subscribed', 'is_approved']

    def get_restaurant_name(self, obj):
        if obj.restaurant:
            return obj.restaurant.name
        return None
    
    def get_subscription(self, obj):
        if obj.restaurant:
            return {'id': obj.subscription.id, 'name': obj.subscription.name, 'price': obj.subscription.price, 'commission_rate':obj.subscription.commission_rate, 'duration': obj.subscription.duration }
        return None


class AdminAdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAdress
        fields = ['line1', 'postal_code', 'city']


class AdminDocSerializer(serializers.ModelSerializer):
    address = AdminAdressSerializer()

    class Meta:
        model = AdminDoc
        fields = ['leagal_name', 'ID_photo', 'business_register', 'address']

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = AdminAdress.objects.create(**address_data)
        admin_doc = AdminDoc.objects.create(address=address, **validated_data)
        return admin_doc