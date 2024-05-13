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


class CategoryApprovalView(generics.UpdateAPIView):
    queryset = CategoryAdminRequest.objects.all()
    serializer_class = CategoryAdminRequestSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the request data includes new name or image
        new_name = request.data.get('name', instance.name)
        new_image = request.data.get('image', instance.image)

        # Check if the request is already accepted
        if instance.is_accepted:
            return Response({"error": "This request has already been accepted."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the instance with the new data
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Check if the request is approved
        if not instance.is_accepted:
            # Create or update the global category based on the updated admin request
            category_data = {
                'name': new_name,
                'image': new_image,
            }
            category_serializer = CategorySerializer(data=category_data)
            if category_serializer.is_valid():
                category_instance = category_serializer.save()
                instance.is_accepted = True  # Update is_accepted to True
                instance.save()
                # Send approval email
                category_request_email_approval(request, instance, is_approved=True)
                return Response(category_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Request updated successfully."}, status=status.HTTP_200_OK)


    

class CategoryAdminRequestRejectView(generics.UpdateAPIView):
    queryset = CategoryAdminRequest.objects.filter(is_accepted=False, is_rejected=False)
    serializer_class = CategoryAdminRequestRejectSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the request includes superadmin_notes
        superadmin_notes = request.data.get('superadmin_notes')

        # Update the instance with the rejection status and notes
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(superadmin_notes=superadmin_notes)
        category_request_email_approval(request, instance, is_approved=False)

        return Response(serializer.data)
    


class CategoriesUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer