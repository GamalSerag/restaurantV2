from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from restaurant_app.models import Category, MenuItem, RestaurantCategory
from .models import Offer

from .serializers import OfferCreateSerializer, OfferDeleteSerializer, OfferUpdateSerializer
from auth_app.permissions import IsAdminOfRestaurant

@permission_classes(IsAdminOfRestaurant)
@api_view(['POST'])
def create_offer_and_associate(request):
    if request.method == 'POST':
        print(request.data)
        serializer = OfferCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save the offer
            offer = serializer.save()

            # Associate the offer with the specified MenuItem or Category
            menu_item_id = request.data.get('menu_item_id')
            category_id = request.data.get('category_id')

            if menu_item_id:
                menu_item = MenuItem.objects.get(pk=menu_item_id)
                if not menu_item.offer :
                    menu_item.offer = offer
                    menu_item.save()
                else: return Response({'error': 'This Item Has Offer'}, status=status.HTTP_400_BAD_REQUEST)
            elif category_id:
                category = RestaurantCategory.objects.get(pk=category_id)
                if not category.offer:
                    category.offer = offer
                    category.save()
                else: return Response({'error': 'This Category Has Offer'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'You must specify either a MenuItem ID or a Category ID'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferUpdateView(generics.UpdateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferUpdateSerializer
    permission_classes = [IsAdminOfRestaurant]

class OfferDeleteView(generics.DestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferDeleteSerializer
    permission_classes = [IsAdminOfRestaurant]