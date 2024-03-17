from django.utils import timezone
from decimal import Decimal
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsCustomer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from restaurant_app.models import MenuItem, Restaurant, SizeAndPrice, MenuItemTypeItem, MenuItemExtraItem
from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer

class CartItemCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]
    def calculate_total_price(self, selected_extra_ids, selected_type_ids, selected_size_and_price_id, quantity):
        try:
            size_and_price_obj = SizeAndPrice.objects.get(id=selected_size_and_price_id)
            base_price = Decimal(size_and_price_obj.price)
        except SizeAndPrice.DoesNotExist:
            raise NotFound({"Error": f"SizeAndPrice with id: {selected_size_and_price_id} does not exist"})

        total_price_with_quantity = base_price  # Total price including quantity
        total_price_without_quantity = base_price  # Total price without considering quantity

        if selected_type_ids:
            for selected_type_id in selected_type_ids:
                selected_type_price = Decimal(MenuItemTypeItem.objects.get(id=selected_type_id).price)
                total_price_with_quantity += selected_type_price
                total_price_without_quantity += selected_type_price

        if selected_extra_ids:
            for selected_extra_id in selected_extra_ids:
                selected_extra_price = Decimal(MenuItemExtraItem.objects.get(id=selected_extra_id).price)
                total_price_with_quantity += selected_extra_price
                total_price_without_quantity += selected_extra_price

        menu_item_obj = size_and_price_obj.menu_item
        restaurant_obj = menu_item_obj.restaurant
            
        total_price_with_quantity *= quantity  # Adjust total price to consider quantity

        return total_price_with_quantity, total_price_without_quantity
    
    def apply_offer(self, total_price, menu_item):
        # Check if there's an active offer for the menu item
        offer = menu_item.offer
        if offer and offer.active_in <= timezone.now() <= offer.expire_in:
            discount = Decimal(offer.discount)
            total_price -= total_price * discount
        return total_price
    
    def post(self, request):

        print(request.data)
        # Retrieve data from request
        menu_item_id = request.data.get('menu_item_id')
        restaurant_id = request.data.get('restaurant_id')
        selected_extra_ids = request.data.get('selected_extra_ids')
        selected_type_ids = request.data.get('selected_type_ids')
        selected_size_and_price_id = request.data.get('selected_size_and_price_id')
        quantity = int(request.data.get('quantity', 1))
        special_instructions = request.data.get('special_instructions') 
        cart_id = request.data.get('cart_id') 
        if cart_id:
            order_mode = Cart.objects.get(pk=cart_id).order_mode
        else: return Response({"error": "Cart with this id doesnot exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the menu item belongs to the requested restaurant
        menu_item = MenuItem.objects.filter(pk=menu_item_id, restaurant_id=restaurant_id).first()
        if not menu_item:
            return Response({"error": "Menu item does not belong to the specified restaurant."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total price
        total_price_before_discount, total_price_before_discount_without_quantity  = self.calculate_total_price(selected_extra_ids, selected_type_ids, selected_size_and_price_id, quantity)
        
        # Apply offer if available
        total_price_after_discount = self.apply_offer(total_price_before_discount, menu_item)
        total_price_after_discount_without_quantity = self.apply_offer(total_price_before_discount_without_quantity, menu_item)
        
        try:
            size = SizeAndPrice.objects.get(id=selected_size_and_price_id).size
            
        except:
            SizeAndPrice.DoesNotExist
            return Response({"Error": f"size_and_price with id: <{selected_size_and_price_id}> does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if a cart item with the same menu item and selected extras and type exists
        try:
            existing_cart_item = CartItem.objects.filter(
                menu_item=menu_item,
                cart__id=cart_id,
                size=size,
                selected_extra_ids=selected_extra_ids,
                selected_type_ids=selected_type_ids
            ).first()
        except ObjectDoesNotExist as e:
            # Handle the case where either the cart item or the menu item does not exist
            existing_cart_item = None  # Or you can set it to whatever makes sense in your context
            if isinstance(e, CartItem.DoesNotExist):
                # Handle the case where the cart item does not exist
                return JsonResponse({'error': 'Cart item does not exist'}, status=400)
            elif isinstance(e, MenuItem.DoesNotExist):
                # Handle the case where the menu item does not exist
                return JsonResponse({'error': 'Menu item does not exist'}, status=400)
        
        if existing_cart_item:
            # If cart item exists, increase its quantity
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
            print(f"<<<<<>><><><><>quantity : {existing_cart_item.quantity}")
            # Calculate the total price difference for the increased quantity
            price_diff_before_discount = existing_cart_item.price * quantity
            price_diff_after_discount = existing_cart_item.price_after_discount * quantity


            # Update cart total price
            print(f"<<<<<>><><><><>cart.total_price before : {existing_cart_item.cart.total_price}")
            existing_cart_item.cart.total_price += price_diff_after_discount
            existing_cart_item.cart.save()

            
            # Update the cart item's total price
            existing_cart_item.total_price_after_discount += price_diff_after_discount
            existing_cart_item.total_price_before_discount += price_diff_before_discount
            existing_cart_item.save()
            print(f"<<<<<>><><><><>cart.total_price after : {existing_cart_item.cart.total_price}")
            # Serialize existing cart item data
            serializer = CartItemSerializer(existing_cart_item)
        else:

            try:    
                # Create cart item
                cart_item = CartItem.objects.create(
                    menu_item=menu_item,
                    cart_id=cart_id,
                    quantity=quantity,
                    price=total_price_before_discount_without_quantity,
                    price_after_discount = total_price_after_discount_without_quantity,
                    size=size,
                    special_instructions=special_instructions,
                    total_price_before_discount=total_price_before_discount,
                    total_price_after_discount=total_price_after_discount,
                    selected_extra_ids=selected_extra_ids,
                    selected_type_ids=selected_type_ids
                    # Add other fields as needed
                )
                # cart_item.cart.total_price += total_price_after_discount
                # Serialize cart item data
                serializer = CartItemSerializer(cart_item)
            
                # Update cart total price
                cart = Cart.objects.get(pk=request.data.get('cart_id'))
                cart.total_price += total_price_after_discount
                if cart.order_mode == 'delivery' and not cart.items.exists():
                    cart.total_price += cart.delivery_fee
                cart.save()
            except ObjectDoesNotExist as e:
                # Handle the case where either the cart item or the menu item does not exist
                if isinstance(e, CartItem.DoesNotExist):
                    return JsonResponse({'error': 'Cart item does not exist'}, status=400)
                elif isinstance(e, MenuItem.DoesNotExist):
                    return JsonResponse({'error': 'Menu item does not exist'}, status=400)
        
        
        # Return serialized cart item data in the response
        return Response(serializer.data)
    

class CartItemUpdateView(generics.UpdateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def update(self, request, *args, **kwargs):
        print(request.data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Get the updated quantity from the request data
        new_quantity = request.data.get('quantity')
        
        
        if new_quantity is not None:
            # Calculate the difference between the new and old quantities
            quantity_diff = int(new_quantity) - instance.quantity

            if quantity_diff > 0:
                print(f'<<<<<<<<<<   quantity_diff = + {quantity_diff}   >>>>>>>>')
                # Increase quantity: Update the total cart price by adding the price difference
                instance.cart.total_price += instance.price_after_discount * quantity_diff
            elif quantity_diff < 0:
                # Decrease quantity: Update the total cart price by subtracting the price difference
                instance.cart.total_price -= instance.price_after_discount * abs(quantity_diff)
                print(f'<<<<<<<<<<   quantity_diff :  -{abs(quantity_diff)}  >>>>>>>>')


            
            # Save the updated cart total price
            instance.cart.save()

            # Update the quantity of the cart item
            instance.quantity = new_quantity
            instance.save()

        # Update the cart item instance with the new data
        self.perform_update(serializer)

        return Response(serializer.data)




class CartCreateView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer



class CartUpdateView(generics.UpdateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    def update(self, request, *args, **kwargs):
        print(request.data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        current_order_mode = instance.order_mode
        order_mode = request.data.get('order_mode') 
        print(order_mode)


        if order_mode:
            # Update the order mode
            instance.order_mode = order_mode

            # Update the total price based on the order mode
            if current_order_mode == 'delivery':
                # Subtract the delivery fee from the total price if switching from delivery mode
                instance.total_price -= instance.delivery_fee
            elif order_mode == 'delivery':
                # Add the delivery fee to the total price if switching to delivery mode
                instance.total_price += instance.delivery_fee

            # Save the changes to the instance
            instance.save()
        
        self.perform_update(serializer)

        return Response(serializer.data)



class CartDetailsView(APIView):
    permission_classes = [IsCustomer]
    
    def get(self, request):
        # Get the authenticated user's customer profile
        customer = request.user.customer_profile

        # Get the restaurant ID from the request data
        restaurant_id = request.query_params.get('restaurant_id')
        
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

        order_mode = request.query_params.get('order_mode')

        # Ensure that the restaurant ID is provided in the request data
        if not restaurant_id:
            return Response({'error': 'Restaurant ID is required in the request data.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the cart based on the customer and restaurant IDs
        cart, created = Cart.objects.get_or_create(customer=customer, restaurant_id=restaurant_id)
        

        if created:
            # Update the order mode if provided in the request
            if order_mode:
                if order_mode.lower() in ['delivery', 'pick_up', 'dine_in']:
                    cart.order_mode = order_mode.lower()
                    if cart.order_mode == 'delivery' :
                        cart.total_price +=  restaurant.delivery_fee
                    cart.save()
                else:
                    cart.delete()
                    return Response({"error": "Invalid order mode. Choose from 'delivery', 'pickup', or 'dine_in'."}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the cart and return the response
        serializer = CartSerializer(cart)
        return Response(serializer.data)



class CartItemDeleteView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Subtract the total cart item price from the cart
        cart = instance.cart
        cart.total_price -= instance.price * instance.quantity
        cart.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)