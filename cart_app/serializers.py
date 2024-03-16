from rest_framework import serializers

from restaurant_app.models import MenuItemExtraItem, MenuItemTypeItem
# from restaurant_app.serializers import MenuItemExtraItemSerializer, MenuItemTypeItemSerializer
from .models import Cart, CartItem





        
class CartItemSerializer(serializers.ModelSerializer):
    selected_extra_items = serializers.SerializerMethodField()
    selected_type_items = serializers.SerializerMethodField()
    name = serializers.CharField(source='menu_item.name')


    def get_selected_extra_items(self, cart_item):
        selected_extra_ids = cart_item.selected_extra_ids
        if selected_extra_ids:
            return MenuItemExtraItem.objects.filter(id__in=selected_extra_ids).values('id', 'name', 'price')
        else:
            return []

    def get_selected_type_items(self, cart_item):
        selected_type_ids = cart_item.selected_type_ids

        if selected_type_ids:
            return MenuItemTypeItem.objects.filter(id__in=selected_type_ids).values('id', 'name', 'price')
        else:
            return []

    class Meta:
        model = CartItem
        fields = ['id', 'cart','name', 'menu_item', 'quantity', 'price', 'price_after_discount', 'total_price_before_discount', 'total_price_after_discount',  'special_instructions', 'size', 'selected_extra_items', 'selected_type_items']



class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()  # Use SerializerMethodField instead of CartItemSerializer
    restaurant_name = serializers.SerializerMethodField()
    discount_values = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'total_price', 'customer', 'notes', 'restaurant_id', 'restaurant_name', 'items', 'order_mode', 'delivery_fee', 'discount_values']


    def get_items(self, obj):
        # Get items queryset and sort by id
        items_queryset = obj.items.all().order_by('id')
        # Serialize sorted items queryset
        return CartItemSerializer(items_queryset, many=True).data
    

    def get_restaurant_name(self, obj):

        return obj.restaurant.name
    

    def get_discount_values(self, obj):
        discount_values = []
        for cart_item in obj.items.all():
            # Calculate the difference between price and price_after_discount
            discount_amount = cart_item.total_price_before_discount - cart_item.total_price_after_discount
            # Check if there's a discount
            if discount_amount > 0:
                # Add cart item name and discount amount as a dictionary to the list
                discount_values.append({'name': cart_item.menu_item.name, 'discount_amount': discount_amount})
        return discount_values
