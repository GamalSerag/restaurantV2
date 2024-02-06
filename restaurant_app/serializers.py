from rest_framework import serializers
from .models import Category, MenuItem, Restaurant


class SizeAndPriceSerializer(serializers.Serializer):
    size = serializers.CharField()
    price = serializers.FloatField()





class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(child=serializers.CharField())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    sizes_and_prices = SizeAndPriceSerializer(many=True, required=False)
    restaurant_id = serializers.IntegerField(write_only=True)  # Added this line

    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'image', 'category', 'ingredients', 'restaurant_id', 'sizes_and_prices')

    def get_image(self, obj):
        # Customize how image URLs are generated
        return self.context['request'].build_absolute_uri(obj.image.url) if obj.image else None
    

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        return representation

    def create(self, validated_data):
        # Extract restaurant_id from the validated data
        restaurant_id = validated_data.pop('restaurant_id', None)

        # Assuming 'restaurant_id' is the correct field name in your model
        restaurant = Restaurant.objects.get(pk=restaurant_id)

        # Add the 'restaurant' instance to the validated data
        validated_data['restaurant'] = restaurant

        # Call the create method of the parent class
        return super().create(validated_data)
    
    def delete(self, instance):
        instance.delete()



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')



class CategoryWithMenuItemsSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, source='menuitem_set')

    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'menu_items')


class RestaurantSerializer(serializers.ModelSerializer):
    categories = CategoryWithMenuItemsSerializer(many=True, required=False)
    # is_subscribed = serializers.BooleanField(source='admin_profile.is_subscribed', read_only=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'logo','background', 'state', 'free_delivery', 'categories',
                  'address', 'open_in', 'close_in', 'order_modes', 'tax',
                     'delivery_fee', 'minimum_order', 'delivery_time', 'latitude', 'longitude', 'country', 'city', 'phone',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Update the categories with the filtered menu items
        for category in representation['categories']:
            category_id = category['id']
            menu_items = MenuItem.objects.filter(restaurant=instance, category__id=category_id)
            menu_items_data = MenuItemSerializer(menu_items, many=True).data
            # Ensure the full path for image URLs in menu items
            for item in menu_items_data:
                if 'image' in item and item['image']:
                    item['image'] = self.context['request'].build_absolute_uri(item['image'])

            category['menu_items'] = menu_items_data
        
        return representation