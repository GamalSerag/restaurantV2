from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from location_app.models import City
from ..models import Category, CategoryAdminRequest, MenuItemExtra, MenuItemExtraItem, MenuItemType, MenuItemTypeItem, Restaurant, MenuItem, RestaurantCategory, SizeAndPrice
from ..serializers import CategoryAdminRequestRejectSerializer, CategoryAdminRequestSerializer, CategorySerializer, MapRestaurantSerializer, MenuItemExtraItemSerializer, MenuItemExtraSerializer, MenuItemTypeItemSerializer, RestaurantCardsSerializer, RestaurantCategorySerializer, RestaurantSerializer, MenuItemSerializer, SearchResultSerializer, SizeAndPriceSerializer
from urllib.parse import unquote
from django.db.models import Q
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from ..service import apply_restaurants_filters
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        # Filter restaurants based on the 'is_subscribed' field
        return Restaurant.objects.filter(admin_profile__is_subscribed=True)
    

class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    def get(self, request, *args, **kwargs):
        # Retrieve the Restaurant instance
        restaurant_instance = self.get_object()


        # Initialize the response data
        response_data = super().get(request, *args, **kwargs).data

        # Include size and price information for each menu item
        for category_data in response_data['categories']:
            for menu_item_data in category_data['menu_items']:
                menu_item_instance = MenuItem.objects.get(id=menu_item_data['id'])
                size_and_prices_data = SizeAndPrice.objects.filter(menu_item=menu_item_instance)
                size_and_prices_serializer = SizeAndPriceSerializer(size_and_prices_data, many=True)
                menu_item_data['sizes_and_prices'] = size_and_prices_serializer.data

        return Response(response_data)
    


class RestaurantListViewByCity(generics.ListAPIView):
    
    # serializer_class = RestaurantSerializer
    serializer_class = RestaurantCardsSerializer
    pagination_class = CustomPagination
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        city_name = self.kwargs['city_name']
        city = get_object_or_404(City, name=city_name)

        queryset = Restaurant.objects.filter(city=city)
        
        queryset = apply_restaurants_filters(queryset, self.request.query_params)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer_context = self.get_serializer_context()

        # Paginate the queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated data
        serializer = self.serializer_class(paginated_queryset, many=True, context=serializer_context)

        # Construct the response with pagination metadata
        return paginator.get_paginated_response(serializer.data)

    def get_serializer_context(self):
        # Include the request object in the serializer context
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class MapRestaurantListViewByCity(generics.ListAPIView):
    serializer_class = MapRestaurantSerializer
    queryset = Restaurant.objects.all()
    
    def get_queryset(self):
        city_name = self.kwargs['city_name']
        city = get_object_or_404(City, name=city_name)
        queryset = Restaurant.objects.filter(city=city)
        return queryset
    



class SearchView(generics.ListAPIView):
    serializer_class = SearchResultSerializer
    pagination_class = CustomPagination  # Assuming you have defined CustomPagination
    restaurant_count, menu_item_count = 0, 0

    

    def get_queryset(self):
        city_name = self.kwargs['city_name']
        city = get_object_or_404(City, name=city_name)
        query = self.request.query_params.get('q', '').strip()
        search_type = self.request.query_params.get('type', '').lower()  # Get the type parameter
        restaurants = Restaurant.objects.filter(city=city, name__icontains=query)
        self.restaurant_count = restaurants.count()

        menu_items = MenuItem.objects.filter(restaurant__city=city, name__icontains=query)
        self.menu_item_count = menu_items.count()

        if search_type == 'restaurant':
            queryset = restaurants
        elif search_type == 'menu_item':
            queryset = menu_items
        else:
            queryset = []
        
            

        if queryset.exists():
            queryset = apply_restaurants_filters(queryset, self.request.query_params)
            if search_type == 'restaurant':
                self.restaurant_count = queryset.count()
            elif search_type == 'menu_item':
                self.menu_item_count = queryset.count()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search_type = self.request.query_params.get('type', '').lower()  # Get the type parameter

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer_context = {'request': request}
        serializer = self.serializer_class(paginated_queryset, many=True, context=serializer_context)

        data = {
            'count': paginator.page.paginator.count,
            'restaurant_count': self.restaurant_count,  # Count all restaurants
            'menu_item_count': self.menu_item_count,  # Count all menu items
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'num_pages': paginator.page.paginator.num_pages,
            'results': serializer.data,
        }
        return Response(data)
    
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        city_name = self.kwargs.get('city_name')
        if city_name == 'All':
            categories = Category.objects.all()
        else:
            categories = Category.objects.filter(restaurant_categories__restaurant__city__name=city_name).distinct()
        return categories
