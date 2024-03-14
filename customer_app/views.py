
from rest_framework import generics, status
from rest_framework.response import Response

from restaurant_app.models import Restaurant
from .models import Customer
from .serializers import CustomerSerializer, FavoriteRestaurantSerializer
from rest_framework.permissions import IsAuthenticated

class CustomerViewSet(generics.RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]




class AddFavoriteRestaurantView(generics.UpdateAPIView):
    serializer_class = CustomerSerializer
    
    def patch(self, request, *args, **kwargs):
        # Get the authenticated customer
        customer = request.user.customer_profile

        # Retrieve the restaurant ID from the request data
        restaurant_id = request.data.get('restaurant_id')

        # Check if the restaurant ID is provided
        if not restaurant_id:
            return Response({"error": "Restaurant ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the restaurant object
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Add the restaurant to the customer's favorites
        customer.favorites.add(restaurant)

        # Serialize and return the updated customer data
        serializer = self.get_serializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class FavoriteRestaurantListView(generics.ListAPIView):
    serializer_class = FavoriteRestaurantSerializer

    def get_queryset(self):
        # Get the authenticated customer
        customer = self.request.user.customer_profile

        # Retrieve the favorite restaurants based on the customer's favorites field
        favorite_restaurant_ids = customer.favorites.all().values_list('id', flat=True)

        # Return the queryset of restaurants with the favorite IDs
        return Restaurant.objects.filter(id__in=favorite_restaurant_ids)