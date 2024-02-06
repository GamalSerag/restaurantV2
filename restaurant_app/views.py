import json
from urllib import request
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from admin_app.models import Admin

from location_app.models import City
from .models import Category, Restaurant, MenuItem
from .serializers import CategorySerializer, RestaurantSerializer, MenuItemSerializer
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsAdminOfRestaurant
from rest_framework import status
from payment_app.serializers import SubscriptionSerializer


class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        # Filter restaurants based on the 'is_subscribed' field
        return Restaurant.objects.filter(admin_profile__is_subscribed=True)
    






class AdminRestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    # permission_classes = [IsAuthenticated, IsAdminOfRestaurant]
    
    def put(self, request, *args, **kwargs):
        print("Data in PUT request:", request.data)
        return super().put(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):

        print(request.data)
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


        return Response(response_data)
    
    


class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    


class RestaurantListViewByCity(generics.ListAPIView):
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        city_name = self.kwargs['city_name']
        city = get_object_or_404(City, name=city_name)

        queryset = Restaurant.objects.filter(city=city)

        # Apply additional filters if provided in the query parameters
        state = self.request.query_params.get('availability')
        
        free_delivery = self.request.query_params.get('free_delivery')
        min_order = self.request.query_params.get('min_order')
        categories_param = self.request.query_params.get('categories', '')
        categories = [category.strip() for category in unquote(categories_param).split(',') if category.strip()]

        if state:
            state = state.capitalize()
            queryset = queryset.filter(state=state)

        if free_delivery:

            queryset = queryset.filter(freeDelivery=free_delivery)

        if min_order:
            queryset = queryset.filter(minimum_order__lte=min_order)
        
        if categories:
            queryset = queryset.filter(categories__name__in=categories).distinct() # if there i more thn one categpry in a restaurant .distinct() returns on object of restaurant 

        return queryset
    

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(f'Deleting instance: {instance}')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class MenuItemCreateView(generics.CreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOfRestaurant]
    print(f'permission_classes = {permission_classes}')
    def perform_create(self, serializer):
        # Call perform_create of the parent class
        instance = serializer.save()

        # Update the restaurant's categories with the new menu item
        restaurant = instance.restaurant
        category = instance.category

        # Check if the category is already associated with the restaurant
        if category not in restaurant.categories.all():
            restaurant.categories.add(category)

            
    def create(self, request, *args, **kwargs):
        print(request.data)
        print(f"Authenticated user: {request.user}")

        sizes_and_prices_str = request.data.get('sizes_and_prices')
        sizes_and_prices_list = json.loads(sizes_and_prices_str)
        print(f"The type of sizes_and_prices_list {type(sizes_and_prices_list)}")

        # Use self.get_serializer instead of modifying request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(f'Validation errors: {serializer.errors}')

        # Update sizes_and_prices in the validated data
        serializer.validated_data['sizes_and_prices'] = sizes_and_prices_list

        # Perform any additional processing needed before creating the object

        self.perform_create(serializer)
        return Response(serializer.data)
    


class MenuItemUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOfRestaurant]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    



class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer




class CityCategoriesView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        city_name = self.kwargs.get('city_name')
        queryset = Category.objects.filter(restaurant__city__name=city_name).distinct()
        return queryset
    
