from rest_framework import serializers

from offers_app.serializers import OfferUpdateSerializer
from .models import Category, MenuItem, MenuItemExtra, MenuItemExtraItem, MenuItemType, MenuItemTypeItem, Restaurant, RestaurantCategory, SizeAndPrice
from django.db.models import Q
from drf_writable_nested.serializers import WritableNestedModelSerializer

class SizeAndPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeAndPrice
        fields = ('id', 'size', 'price')





class MenuItemExtraItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItemExtraItem
        fields = ('id', 'name', 'price')

    

class MenuItemExtraSerializer(serializers.ModelSerializer):
    items = MenuItemExtraItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItemExtra
        fields = ('id', 'title', 'items')
        extra_kwargs = {
            'title': {'required': False}
        }



class MenuItemTypeItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItemTypeItem
        fields = ('id', 'name', 'price')

    
class MenuItemTypeSerializer(serializers.ModelSerializer):
    items = MenuItemTypeItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItemType
        fields = ('id', 'title', 'items')
        extra_kwargs = {
            'title': {'required': False}
        }


class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(child=serializers.CharField(), required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=RestaurantCategory.objects.all())
    sizes_and_prices = SizeAndPriceSerializer(many=True, read_only=True)
    # sizes_and_prices = serializers.ListSerializer(child=SizeAndPriceSerializer(), required=False)    
    restaurant_id = serializers.IntegerField(write_only=True)
    offer = OfferUpdateSerializer(read_only=True)
    extras = MenuItemExtraSerializer(many=True, required=False)
    types = MenuItemTypeSerializer(many=True, required=False)
    
        
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'image', 'category', 'ingredients', 'restaurant_id', 'sizes_and_prices', 'offer', 'extras', 'types')

    def get_image(self, obj):
        # Customize how image URLs are generated
        return self.context['request'].build_absolute_uri(obj.image.url) if obj.image else None

    def create(self, validated_data):
        sizes_and_prices_data = validated_data.pop('sizes_and_prices', [])  # Extract sizes_and_prices data
        extras_data = validated_data.pop('extras', [])
        types_data = validated_data.pop('types', [])
        menu_item = MenuItem.objects.create(**validated_data)  # Create MenuItem instance
        
        # Create SizeAndPrice instances for each dictionary in sizes_and_prices_data
        for size_price_data in sizes_and_prices_data:
            SizeAndPrice.objects.create(menu_item=menu_item, **size_price_data)
        
        # Create Extra instances and associated ExtraItem instances
        for extra_data in extras_data:
            items_data = extra_data.pop('items', [])
            print(f"Extra Data: {extra_data}")  # Debugging
            extra = MenuItemExtra.objects.create(**extra_data)
            
            for item_data in items_data:
                MenuItemExtraItem.objects.create(extra=extra, **item_data)

        # Create type instances and associated typeItem instances
        for type_data in types_data:
            items_data = type_data.pop('items', [])
            print(f"Types Data: {type_data}")  # Debugging
            type_instence = MenuItemType.objects.create(**type_data)
            
            for item_data in items_data:
                MenuItemTypeItem.objects.create(type=type_instence, **item_data)

        return menu_item
    


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.category = validated_data.get('category', instance.category)
        instance.ingredients = validated_data.get('ingredients', instance.ingredients)

        print('################################################################################################################################################################################################################################################################################################################################################################################################################################################################')
        # Handle updates for extras
        print(' ')
        print(' ')
        print(' ')
        # print (validated_data)
        # print(' ')
        # print(' ')
        # print(' ')
        extras_data = validated_data.pop('extras', None)
        # print(extras_data)
        # print(type(extras_data))
        # print((extras_data[0]))
        # print(type(extras_data[0]))
        # print((extras_data[1]))
        # print(type(extras_data[1]))
        
        
        for key, value in extras_data[0].items(): 
            print('VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV')
            print(key, value) 
        
        

        print(f'extras_data in serializer :::::: {extras_data[0].values}')
        if extras_data is not None:
            for extra_data in extras_data:
                items_data = extra_data.pop('items', [])
                extra_id = extra_data.pop('id', None)
                if extra_id:
                    extra_instance = MenuItemExtra.objects.get(id=extra_id)
                    for item_data in items_data:
                        print(item_data)
                        # Update or create the MenuItemExtraItem instances
                        MenuItemExtraItem.objects.update_or_create(extra=extra_instance, **item_data)

        # Handle updates for types
        types_data = validated_data.pop('types', None)
        if types_data is not None:
            for type_data in types_data:
                type_id = type_data.pop('id', None)
                if type_id:
                    type_instance, _ = MenuItemType.objects.get_or_create(id=type_id, defaults=type_data)

                    # Handle the items
                    items_data = type_data.pop('items', [])
                    for item_data in items_data:
                        MenuItemTypeItem.objects.update_or_create(extra=type_instance, **item_data)
                    instance.types.add(type_instance)

        instance.save()  # Save the instance after all updates
        return instance
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')



class RestaurantCategorySerializer(serializers.ModelSerializer):
    # category_id = serializers.IntegerField(source='category.id')
    category_type = serializers.CharField(source='category.name', required= False)
    category_image = serializers.ImageField(source='category.image',required= False)
    menu_items = MenuItemSerializer(many=True, read_only=True)
    offer = serializers.SerializerMethodField()

    
    
    class Meta:
        model = RestaurantCategory
        fields = ('id','name', 'category_type','category_image', 'menu_items', 'offer', 'tax', 'is_active')

    
    
    def get_offer(self, obj):
        # Custom logic to retrieve and format the offer associated with the restaurant category
        if obj.offer:
            # Assuming obj.offer is the related offer instance
            offer_data = {
                'id': obj.offer.id, 
                'title': obj.offer.title,
                'description': obj.offer.description,
                "active_in":obj.offer.active_in,
                "expire_in":obj.offer.expire_in,
                "discount" :obj.offer.discount
            }
            return offer_data
        else:
            return None


class RestaurantSerializer(serializers.ModelSerializer):
    categories = RestaurantCategorySerializer(many=True, required=False, source='restaurantcategory_set')  # Serialize restaurant categories
    order_modes = serializers.ListField(child=serializers.CharField())
    
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'logo','background', 'state', 'free_delivery', 'categories',
                  'address', 'open_in', 'close_in', 'order_modes', 'tax',
                     'delivery_fee', 'minimum_order', 'delivery_time', 'latitude', 'longitude', 'country', 'city', 'phone',)

    
    
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     # Update the categories with the filtered menu items
    #     for category in representation['categories']:
    #         category_id = category['id']
    #         menu_items = MenuItem.objects.filter(restaurant=instance, category__id=category_id)
    #         menu_items_data = MenuItemSerializer(menu_items, many=True).data
    #         # Ensure the full path for image URLs in menu items
    #         for item in menu_items_data:
    #             if 'image' in item and item['image']:
    #                 item['image'] = self.context['request'].build_absolute_uri(item['image'])

    #         category['menu_items'] = menu_items_data
        
    #     return representation