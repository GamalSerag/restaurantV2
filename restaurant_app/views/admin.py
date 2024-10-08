import json
from rest_framework.exceptions import ValidationError
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from admin_app.models import Admin

from location_app.models import City
from offers_app.models import Offer
from ..models import Category, CategoryAdminRequest, MenuItemExtra, MenuItemExtraItem, MenuItemType, MenuItemTypeItem, Restaurant, MenuItem, RestaurantCategory, SizeAndPrice
from ..serializers import CategoryAdminRequestRejectSerializer, CategoryAdminRequestSerializer, CategorySerializer, MenuItemExtraItemSerializer, MenuItemExtraSerializer, MenuItemTypeItemSerializer, RestaurantCardsSerializer, RestaurantCategorySerializer, RestaurantSerializer, MenuItemSerializer, SearchResultSerializer, SizeAndPriceSerializer
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsAdminOfRestaurant
from rest_framework import status
from payment_app.serializers import SubscriptionSerializer
from rest_framework.request import Request
from rest_framework import serializers
from django.db import transaction
from django.db.models import Q
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from ..utils import category_request_email_approval
from rest_framework.pagination import PageNumberPagination
from django.db import IntegrityError

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AdminRestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get(self, request, *args, **kwargs):
        # Retrieve the Restaurant instance
        restaurant_instance = self.get_object()

        # Check if there is an associated Admin instance
        admin_instance = Admin.objects.filter(restaurant=restaurant_instance).first()

        # Initialize the response data
        response_data = super().get(request, *args, **kwargs).data

        # If Admin instance exists, include is_subscribed in the response
        if admin_instance:
            response_data['is_subscribed'] = admin_instance.is_subscribed

            # Serialize the subscription instance
            subscription_serializer = SubscriptionSerializer(admin_instance.subscription)
            serialized_subscription = subscription_serializer.data
            response_data['subscription'] = serialized_subscription

        # Include size and price information for each menu item
        for category_data in response_data['categories']:
            for menu_item_data in category_data['menu_items']:
                menu_item_instance = MenuItem.objects.get(id=menu_item_data['id'])
                size_and_prices_data = SizeAndPrice.objects.filter(menu_item=menu_item_instance)
                size_and_prices_serializer = SizeAndPriceSerializer(size_and_prices_data, many=True)
                menu_item_data['sizes_and_prices'] = size_and_prices_serializer.data

        return Response(response_data)

    def put(self, request, *args, **kwargs):
        print(request.data)
        instance = self.get_object()

        order_modes = []
        for key, value in request.data.items():
            if key.startswith('order_modes'):
                order_modes.append(value)

        # Update order_modes if there are any in the request
        if order_modes:
            instance.order_modes = order_modes
            instance.save()

        # Update other fields
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    


class MenuItemCreateView(generics.CreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOfRestaurant]
    print(f'permission_classes = {permission_classes}')
    
    def perform_create(self, serializer):
        # Retrieve the admin associated with the authenticated user
        admin = self.request.user.admin_profile

        # Retrieve the associated restaurant from the admin
        restaurant = admin.restaurant
        print(f"restaurant = {restaurant.name}")
        # Extract the category ID from the request data
        category_id = self.request.data.get('category')
        print(f'category_id = {category_id}')
        # Retrieve the restaurant category associated with the provided category ID and the restaurant
        restaurant_category = RestaurantCategory.objects.filter(restaurant=restaurant, id=category_id).first()
        print(f"restaurant_category = {restaurant_category}")
        # Ensure that the restaurant category exists and is associated with the restaurant
        if not restaurant_category:
            raise serializers.ValidationError({'error': 'Invalid category ID'})

        # Extract size and price data from request
        sizes_and_prices_data = []
        extras_data = []
        types_data = []

        for key, value in self.request.data.items():
            if key.startswith('sizes_and_prices'):
                # Extract index from key
                idx = int(key.split('[')[1].split(']')[0])

                # Check if the key represents a size or price
                if key.endswith('size]'):
                    size = value
                    price_key = f'sizes_and_prices[{idx}][price]'
                    price = self.request.data.get(price_key)
                    if price is not None:
                        sizes_and_prices_data.append({'size': size, 'price': price})
                    else:
                        raise serializers.ValidationError({'error': f'Missing price for size {size}'})
                
                
            elif key.startswith('extras'):
                extra_idx = int(key.split('[')[1].split(']')[0])
                if extra_idx >= len(extras_data):
                    extras_data.append({'title': None, 'items': []})

                if key.endswith('title]'):
                    extras_data[extra_idx]['title'] = value
                elif 'items' in key and key.endswith('price]'):
                    item_idx = len(extras_data[extra_idx]['items'])
                    name_key = f'extras[{extra_idx}][items][{item_idx}][name]'
                    name = self.request.data.get(name_key)
                    if name is None:
                        raise serializers.ValidationError({'error': f'Missing name for item {item_idx}'})
                    extras_data[extra_idx]['items'].append({'name': name, 'price': value})
            
            
            elif key.startswith('types') :#and value != "null"
                
                type_idx = int(key.split('[')[1].split(']')[0])
                if type_idx >= len(types_data):
                    types_data.append({'title': None, 'items': []})

                if key.endswith('title]'):
                    types_data[type_idx]['title'] = value
                elif 'items' in key and key.endswith('price]'):
                    item_idx = len(types_data[type_idx]['items'])
                    name_key = f'types[{type_idx}][items][{item_idx}][name]'
                    name = self.request.data.get(name_key)
                    if name is None:
                        raise serializers.ValidationError({'error': f'Missing name for item {item_idx}'})
                    types_data[type_idx]['items'].append({'name': name, 'price': value})
            

        print(f':::@@:::types_data: {types_data}')
        # Save the MenuItem instance
        menu_item = serializer.save(restaurant=restaurant, category=restaurant_category)

        # Create SizeAndPrice instances for each pair of size and price
        for size_price_data in sizes_and_prices_data:
            SizeAndPrice.objects.create(menu_item=menu_item, **size_price_data)

        # Create MenuItemExtra instances and their associated MenuItemExtraItem instances
        for extra_data in extras_data:
            items_data = extra_data.pop('items', [])
            extra = MenuItemExtra.objects.create(**extra_data)
            for item_data in items_data:
                MenuItemExtraItem.objects.create(extra=extra, **item_data)
            # Associate the created MenuItemExtra with the MenuItem
            menu_item.extras.add(extra)

        # Create MenuItemType instances and their associated MenuItemTypeItem instances
        for type_data in types_data:
            items_data = type_data.pop('items', [])
            type = MenuItemType.objects.create(**type_data)
            for item_data in items_data:
                MenuItemTypeItem.objects.create(type=type, **item_data)
            # Associate the created MenuItemType with the MenuItem
            menu_item.types.add(type)


class MenuItemCreateView(generics.CreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]
    # print(f'permission_classes = {permission_classes}')
    
    # def perform_create(self, serializer):
    #     # Retrieve the admin associated with the authenticated user
    #     admin = self.request.user.admin_profile

    #     # Retrieve the associated restaurant from the admin
    #     restaurant = admin.restaurant
    #     print(f"restaurant = {restaurant.name}")
    #     # Extract the category ID from the request data
    #     category_id = self.request.data.get('category')
    #     print(f'category_id = {category_id}')
    #     # Retrieve the restaurant category associated with the provided category ID and the restaurant
    #     restaurant_category = RestaurantCategory.objects.filter(restaurant=restaurant, id=category_id).first()
    #     print(f"restaurant_category = {restaurant_category}")
    #     # Ensure that the restaurant category exists and is associated with the restaurant
    #     if not restaurant_category:
    #         raise serializers.ValidationError({'error': 'Invalid category ID'})

    #     # Extract size and price data from request
    #     sizes_and_prices_data = []
    #     extras_data = []
    #     types_data = []

    #     for key, value in self.request.data.items():
    #         if key.startswith('sizes_and_prices'):
    #             # Extract index from key
    #             idx = int(key.split('[')[1].split(']')[0])

    #             # Check if the key represents a size or price
    #             if key.endswith('size]'):
    #                 size = value
    #                 price_key = f'sizes_and_prices[{idx}][price]'
    #                 price = self.request.data.get(price_key)
    #                 if price is not None:
    #                     sizes_and_prices_data.append({'size': size, 'price': price})
    #                 else:
    #                     raise serializers.ValidationError({'error': f'Missing price for size {size}'})
                
                
    #         elif key.startswith('extras'):
    #             extra_idx = int(key.split('[')[1].split(']')[0])
    #             if extra_idx >= len(extras_data):
    #                 extras_data.append({'title': None, 'items': []})

    #             if key.endswith('title]'):
    #                 extras_data[extra_idx]['title'] = value
    #             elif 'items' in key and key.endswith('price]'):
    #                 item_idx = len(extras_data[extra_idx]['items'])
    #                 name_key = f'extras[{extra_idx}][items][{item_idx}][name]'
    #                 name = self.request.data.get(name_key)
    #                 if name is None:
    #                     raise serializers.ValidationError({'error': f'Missing name for item {item_idx}'})
    #                 extras_data[extra_idx]['items'].append({'name': name, 'price': value})
            
            
    #         elif key.startswith('types') :#and value != "null"
                
    #             type_idx = int(key.split('[')[1].split(']')[0])
    #             if type_idx >= len(types_data):
    #                 types_data.append({'title': None, 'items': []})

    #             if key.endswith('title]'):
    #                 types_data[type_idx]['title'] = value
    #             elif 'items' in key and key.endswith('price]'):
    #                 item_idx = len(types_data[type_idx]['items'])
    #                 name_key = f'types[{type_idx}][items][{item_idx}][name]'
    #                 name = self.request.data.get(name_key)
    #                 if name is None:
    #                     raise serializers.ValidationError({'error': f'Missing name for item {item_idx}'})
    #                 types_data[type_idx]['items'].append({'name': name, 'price': value})
            

    #     print(f':::@@:::types_data: {types_data}')
    #     # Save the MenuItem instance
    #     menu_item = serializer.save(restaurant=restaurant, category=restaurant_category)

    #     # Create SizeAndPrice instances for each pair of size and price
    #     for size_price_data in sizes_and_prices_data:
    #         SizeAndPrice.objects.create(menu_item=menu_item, **size_price_data)

    #     # Create MenuItemExtra instances and their associated MenuItemExtraItem instances
    #     for extra_data in extras_data:
    #         items_data = extra_data.pop('items', [])
    #         extra = MenuItemExtra.objects.create(**extra_data)
    #         for item_data in items_data:
    #             MenuItemExtraItem.objects.create(extra=extra, **item_data)
    #         # Associate the created MenuItemExtra with the MenuItem
    #         menu_item.extras.add(extra)

    #     # Create MenuItemType instances and their associated MenuItemTypeItem instances
    #     for type_data in types_data:
    #         items_data = type_data.pop('items', [])
    #         type = MenuItemType.objects.create(**type_data)
    #         for item_data in items_data:
    #             MenuItemTypeItem.objects.create(type=type, **item_data)
    #         # Associate the created MenuItemType with the MenuItem
    #         menu_item.types.add(type)


    

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)

    #     if serializer.is_valid():
    #         print(f'validated_data : {serializer.validated_data}')
    #     else:
    #         print(serializer.errors)
            
        
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def process_extras_types_sizes_prices(data):
    sizes_and_prices_data = []
    extras_data = []
    types_data = []


    
    for key, value in data.items():
        
        if key.startswith('extras'):
            extra_idx = int(key.split('[')[1].split(']')[0])
            
            if extra_idx >= len(extras_data):
                extras_data.append({'id': None, 'title': None, 'items': []})

            if key.endswith('title]'):
                extras_data[extra_idx]['title'] = value
            elif key.endswith('[price]'):
                item_idx = len(extras_data[extra_idx]['items'])
                
                name_key = f'extras[{extra_idx}][items][{item_idx}][name]'
                name = data.get(name_key)
                price_key = f'extras[{extra_idx}][items][{item_idx}][price]'
                price = data.get(price_key)
                if name is None:
                    raise serializers.ValidationError({'error': f'Missing name for extra item {item_idx}'})
                if price is None:
                    raise serializers.ValidationError({'error': f'Missing price for extra item {item_idx}'})
                # Create a new MenuItemExtra instance if ID is not provided
                extra_id_key = f'extras[{extra_idx}][extra_id]'
                
                extra_id = data.get(extra_id_key)
                
                if extra_id is None:
                    menu_item = MenuItem.objects.get(id=data.get('menu_item_id'))
                    extra_instance = MenuItemExtra.objects.create(title=extras_data[extra_idx]['title'])
                    menu_item.extras.add(extra_instance)
                    
                    # Assign the ID back to the extras_data dictionary
                    extras_data[extra_idx]['id'] = extra_instance.id
                else:
                    extra_instance = MenuItemExtra.objects.get(id=extra_id)
                # Check if the item already exists based on its ID
                item_id_key = f'extras[{extra_idx}][items][{item_idx}][id]'
                item_id = data.get(item_id_key)
                
                if item_id:
                    item_instance = MenuItemExtraItem.objects.filter(extra=extra_instance, id=item_id).first()
                    item_instance.name = name
                    item_instance.price = price
                    item_instance.save()
                else:
                    item_instance = None
                if item_instance:
                    # If the item already exists, retrieve its ID
                    item_id = item_instance.id
                else:
                    # If the item does not exist, create a new one
                    item_instance = MenuItemExtraItem.objects.create(extra=extra_instance, name=name, price=price)
                    item_id = item_instance.id
                extras_data[extra_idx]['items'].append({'id': item_id, 'name': name, 'price': price})




        elif key.startswith('types'):
            type_idx = int(key.split('[')[1].split(']')[0])

            if type_idx >= len(types_data):
                types_data.append({'id': None, 'title': None, 'items': []})

            if key.endswith('title]'):
                types_data[type_idx]['title'] = value
            elif key.endswith('[price]'):
                item_idx = len(types_data[type_idx]['items'])

                name_key = f'types[{type_idx}][items][{item_idx}][name]'
                name = data.get(name_key)
                price_key = f'types[{type_idx}][items][{item_idx}][price]'
                price = data.get(price_key)
                if name is None:
                    raise serializers.ValidationError({'error': f'Missing name for type item {item_idx}'})
                if price is None:
                    raise serializers.ValidationError({'error': f'Missing price for type item {item_idx}'})

                type_id_key = f'types[{type_idx}][type_id]'
                type_id = data.get(type_id_key)
                print('')
                print(f'{type_id}')
                print('')

                if type_id is None:
                    menu_item = MenuItem.objects.get(id=data.get('menu_item_id'))
                    type_instance = MenuItemType.objects.create(title=types_data[type_idx]['title'])
                    menu_item.types.add(type_instance)

                    # Assign the ID back to the types_data dictionary
                    types_data[type_idx]['id'] = type_instance.id
                else:
                    type_instance = MenuItemType.objects.get(id=type_id)
                
                item_id_key = f'types[{type_idx}][items][{item_idx}][id]'
                item_id = data.get(item_id_key)

                print(f'type_instance.id : {type_instance.id}')
                print(f'{item_id}')
                print('')

                if item_id:
                    item_instance = MenuItemTypeItem.objects.filter(type=type_instance, id=item_id).first()
                    print(item_instance)
                    item_instance.name = name
                    item_instance.price = price
                    item_instance.save()
                else:
                    item_instance = None
                if item_instance:
                    # If the item already exists, retrieve its ID
                    item_id = item_instance.id
                else:
                    # If the item does not exist, create a new one
                    item_instance = MenuItemTypeItem.objects.create(type=type_instance, name=name, price=price)
                    item_id = item_instance.id
                types_data[type_idx]['items'].append({'id': item_id, 'name': name, 'price': price})

    return sizes_and_prices_data, extras_data, types_data


class MenuItemExtraDeleteView(generics.DestroyAPIView):
    queryset = MenuItemExtra.objects.all()
    serializer_class = MenuItemExtraSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]


class MenuItemExtraItemDeleteView(generics.DestroyAPIView):
    queryset = MenuItemExtraItem.objects.all()
    serializer_class = MenuItemExtraItemSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]

class MenuItemTypeDeleteView(generics.DestroyAPIView):
    queryset = MenuItemType.objects.all()
    serializer_class = MenuItemExtraSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]


class MenuItemTypeItemDeleteView(generics.DestroyAPIView):
    queryset = MenuItemTypeItem.objects.all()
    serializer_class = MenuItemTypeItemSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # offer_id = instance.offer
        # offer = Offer.objects.get(id=offer_id)

        # Fetch related SizeAndPrice instances
        sizes_and_prices = SizeAndPrice.objects.filter(menu_item=instance)
        size_and_price_serializer = SizeAndPriceSerializer(sizes_and_prices, many=True)

        # Include sizes_and_prices in the response data
        response_data = serializer.data
        response_data['sizes_and_prices'] = size_and_price_serializer.data
        # response_data['offer'] = offer

        return Response(response_data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f'Deleting instance: {instance}')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class MenuItemUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]

    # def perform_update(self, serializer):
    #     # Retrieve the admin associated with the authenticated user
    #     admin = self.request.user.admin_profile

    #     # Retrieve the associated restaurant from the admin
    #     restaurant = admin.restaurant
    #     print(f"restaurant = {restaurant.name}")
    #     # Extract the category ID from the request data
    #     category_id = self.request.data.get('category')
    #     print(f'category_id = {category_id}')
    #     # Retrieve the restaurant category associated with the provided category ID and the restaurant
    #     restaurant_category = RestaurantCategory.objects.filter(restaurant=restaurant, id=category_id).first()
    #     print(f"restaurant_category = {restaurant_category}")
    #     # Ensure that the restaurant category exists and is associated with the restaurant
    #     if not restaurant_category:
    #         raise serializers.ValidationError({'error': 'Invalid category ID'})

    #     sizes_and_prices_data, extras_data, types_data = process_extras_types_sizes_prices(self.request.data)

    #     print(f':::::::From views sizes_and_prices_data data : {sizes_and_prices_data}')
    #     print(f':::::::From views Extras data : {extras_data}')
    #     print(f':::::::From views Types data : {types_data}')
            
        
    #     # Save the MenuItem instance
        
    #     menu_item = serializer.save(restaurant=restaurant, category=restaurant_category)

    #     # Create SizeAndPrice instances for each pair of size and price
    #     for size_price_data in sizes_and_prices_data:
    #         SizeAndPrice.objects.update_or_create(menu_item=menu_item, **size_price_data)


    #     for extra_data in extras_data:
    #         items_data = extra_data.pop('items', [])
    #         extra_id = extra_data.pop('id', None)
    #         if extra_id:
    #             extra_instance = MenuItemExtra.objects.get(id=extra_id)  # This line can raise MultipleObjectsReturned error
    #             for item_data in items_data:
    #                 # Use filter() instead of get() to handle multiple results
    #                 extra_items = MenuItemExtraItem.objects.filter(extra=extra_instance, **item_data)
    #                 for extra_item in extra_items:
    #                     # Update or create the MenuItemExtraItem instances
    #                     MenuItemExtraItem.objects.update_or_create(extra=extra_instance, **item_data)

    #     # Update or create MenuItemExtra instances and their associated MenuItemExtraItem instances
    #     for type_data in types_data:
    #         items_data = type_data.pop('items', [])
    #         type_id = type_data.pop('id', None)
    #         if type_id:
    #             type_instance = MenuItemType.objects.get(id=type_id)  
    #             for item_data in items_data:
    #                 # Use filter() instead of get() to handle multiple results
    #                 type_items = MenuItemTypeItem.objects.filter(type=type_instance, **item_data)
    #                 for type_item in type_items:
    #                     # Update or create the MenuItemTypeItem instances
    #                     MenuItemTypeItem.objects.update_or_create(type=type_instance, **item_data)

    #     print("MenuItem data after processing:", menu_item.__dict__)



    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print(f"Data sent to the serializer : {request.data}")
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    


class CategoryAdminRequestView(generics.ListCreateAPIView):
    serializer_class = CategoryAdminRequestSerializer

    def get_queryset(self):
        queryset = CategoryAdminRequest.objects.filter(is_accepted=False, is_rejected=False)
        return queryset

    def perform_create(self, serializer):
        # Set the requested_by field to the authenticated user's admin profile
        serializer.save(requested_by=self.request.user.admin_profile)


class RestaurantCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = RestaurantCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOfRestaurant]

    def get_queryset(self):
        admin = self.request.user.admin_profile
        restaurant_id = admin.restaurant.id
        queryset = RestaurantCategory.objects.filter(restaurant_id=restaurant_id)
        return queryset

    def perform_create(self, serializer):
        admin = self.request.user.admin_profile
        restaurant = admin.restaurant
        serializer.save(restaurant=restaurant)

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError:
            # Handle uniqueness constraint violation
            error_message = "This combination of restaurant and category already exists."
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # Get the filtered queryset
        serializer = self.get_serializer(queryset, many=True)  # Serialize the queryset
        return Response(serializer.data)  # Return the serialized data


class RestaurantCategoryUpdateView(generics.UpdateAPIView):

    serializer_class = RestaurantCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOfRestaurant]
    queryset = RestaurantCategory.objects.all()

    def get_queryset(self):
        admin = self.request.user.admin_profile
        restaurant_id = admin.restaurant.id
        queryset = RestaurantCategory.objects.filter(restaurant_id=restaurant_id)
        return queryset
    
    def put(self, request, *args, **kwargs):

        print(request.data)
        # Get the instance to update
        instance = self.get_object()
        
        # Serialize the instance
        serializer = self.get_serializer(instance, data=request.data)
        
        # Validate and save the serializer
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return a response indicating success
        return Response(serializer.data)

class RestaurantCategoryDeleteView(generics.DestroyAPIView):
    serializer_class = RestaurantCategorySerializer
    queryset = RestaurantCategory.objects.all()


