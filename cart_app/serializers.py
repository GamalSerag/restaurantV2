from rest_framework import serializers
from .models import CartItem



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'timestamps', 'total_price', 'customer', 'notes', 'service', 'restaurant']


        
class CartItemSerializer(serializers.ModelSerializer):
    total_price_before_discount = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_price_after_discount = serializers.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'menu_item', 'quantity', 'price', 'special_instructions', 'size', 'total_price_before_discount', 'total_price_after_discount']

    def create(self, validated_data):
        return CartItem.objects.create(**validated_data)

