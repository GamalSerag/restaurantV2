from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from location_app.models import City
from .models import Category, Restaurant, MenuItem
from .serializers import CategorySerializer, CityCategorySerializer, RestaurantSerializer, MenuItemSerializer
from urllib.parse import unquote

class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer





class RestaurantDetailView(generics.RetrieveAPIView):
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
    

class MenuItemDetailView(generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class CityCategoriesView(generics.ListAPIView):
    serializer_class = CityCategorySerializer

    def get_queryset(self):
        city_name = self.kwargs.get('city_name')
        queryset = Category.objects.filter(restaurant__city__name=city_name).distinct()
        return queryset