
from rest_framework import serializers

from .models import Category, MenuItem, Restaurant







class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(child=serializers.CharField())
    category = serializers.StringRelatedField()

    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description','image', 'category', 'ingredients', 'price', 'restaurant')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation



class CityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')



class CategorySerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, source='menuitem_set')

    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'menu_items')

class RestaurantSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'logo','background', 'state', 'freeDelivery', 'categories', 'address', 'open_in', 'close_in', 'order_modes', 'tax', 'delivery_fee', 'minimum_order', 'delivery_time', 'latitude', 'longitude', 'country', 'city')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Fetch and serialize menu items related to the current restaurant
        # menu_items = MenuItem.objects.filter(restaurant=instance)
        # menu_items_data = MenuItemSerializer(menu_items, many=True).data
        
        # Update the categories with the filtered menu items
        for category in representation['categories']:
            category_id = category['id']
            menu_items = MenuItem.objects.filter(restaurant=instance, category__id=category_id)
            menu_items_data = MenuItemSerializer(menu_items, many=True).data
            
            category['menu_items'] = menu_items_data
        
        return representation