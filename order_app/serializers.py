from rest_framework import serializers

from restaurant_app.models import Restaurant
from .models import DeliveryDetails, Order, OrderInvoice
from drf_writable_nested import WritableNestedModelSerializer
from django.utils.translation import gettext_lazy as _


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ( 'name', 'logo')


class DeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDetails
        fields = '__all__'
        extra_kwargs = {
            'order': {'required': False},
            'post_code': {'required': False},
            'city': {'required': False},
            'area': {'required': False},
            'lane': {'required': False},
            'street_name': {'required': False},
            'house_number': {'required': False},
            'floor': {'required': False},
            'company_name': {'required': False},

        }

        
class OrderSerializer(WritableNestedModelSerializer):
    delivery_details = DeliveryDetailsSerializer()
    restaurant = RestaurantSerializer(required=False)
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'customer': {'required': False},

        }



class OrderInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInvoice
        fields = '__all__'