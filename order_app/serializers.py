from rest_framework import serializers
from .models import DeliveryDetails, Order, OrderInvoice
from drf_writable_nested import WritableNestedModelSerializer
from django.utils.translation import gettext_lazy as _




class DeliveryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDetails
        fields = '__all__'
        extra_kwargs = {
            'order': {'required': False},
        }

        
class OrderSerializer(WritableNestedModelSerializer):
    delivery_details = DeliveryDetailsSerializer()
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