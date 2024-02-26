from datetime import timezone
from decimal import Decimal
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from restaurant_app.models import MenuItem, SizeAndPrice, MenuItemTypeItem, MenuItemExtra
from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer

class AddCartItemView(APIView):
    def calculate_total_price(self, selected_extra_ids, selected_type_ids, selected_size_and_price_id):
        # Calculate total price based on menu item, extras, type, and size
        total_price = Decimal(SizeAndPrice.objects.get(id=selected_size_and_price_id).first().price)
        for selected_type_id in selected_type_ids:
            total_price += Decimal(MenuItemTypeItem.objects.get(id=selected_type_id).first().price)
        
        for extra_id in selected_extra_ids:
            total_price += Decimal(MenuItemExtra.objects.get(id=extra_id).first().price)
        return total_price
    
    def apply_offer(self, total_price, menu_item):
        # Check if there's an active offer for the menu item
        offer = menu_item.offer
        if offer and offer.active_in <= timezone.now() <= offer.expire_in:
            discount = Decimal(offer.discount)
            total_price -= total_price * discount
        return total_price
    
    def post(self, request):
        # Retrieve data from request
        menu_item_id = request.data.get('menu_item_id')
        selected_extra_ids = request.data.getlist('selected_extra_ids')
        selected_type_id = request.data.getlist('selected_type_ids')
        selected_size_and_price_id = request.data.get('selected_size_and_price_id')
        quantity = int(request.data.get('quantity', 1))
        # special_instructions = request.data.get(special_instructions)
        
        # Fetch the menu item
        menu_item = MenuItem.objects.get(pk=menu_item_id)
        
        # Calculate total price
        total_price_before_discount = self.calculate_total_price(selected_extra_ids, selected_type_id, selected_size_and_price_id)
        
        # Apply offer if available
        total_price_after_discount = self.apply_offer(total_price_before_discount, menu_item)
        
        size = SizeAndPrice.objects.get(id=selected_size_and_price_id).first().size
        # Create cart item
        cart_item = CartItem.objects.create(
            menu_item=menu_item,
            quantity=quantity,
            price=total_price_after_discount,
            size=size,
            # special_instructions = special_instructions
            # Add other fields as needed
        )
        
        # Update cart total price
        cart = Cart.objects.get(pk=request.data.get('cart_id'))
        cart.total_price += total_price_after_discount
        cart.save()
        
        # Serialize cart item data
        serializer = CartItemSerializer(cart_item)
        
        # Return serialized cart item data in the response
        return Response(serializer.data)
    


class CartCreateView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
