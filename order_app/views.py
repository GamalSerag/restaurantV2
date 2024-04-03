from datetime import timezone
import json
import time
from django.conf import settings
from rest_framework import generics, views
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from django.views import View
import stripe
from rest_framework import serializers, status
from rest_framework.response import Response

from auth_app.models import User
from order_app.serializers import DeliveryDetailsSerializer, OrderInvoiceSerializer, OrderSerializer
from order_app.utils import send_order_placed_email, send_order_status_changed_email
from .models import DeliveryDetails, Order, OrderInvoice
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse
from  rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsAdminOfRestaurant, IsCustomer
from rest_framework.pagination import PageNumberPagination
from django.db.models.signals import post_save
# from django_cron import CronJobBase, Schedule

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY 

def download_pdf(request):
    pdf_path = 'D:/books/Two Scoops of Django 3.x_ Best Practices for the Django Web Framework by Daniel Feldroy.pdf'
    response = FileResponse(open(pdf_path, 'rb'), as_attachment=True)
    return response

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # Assign the authenticated user's ID as the customer ID
        serializer.save(customer=self.request.user.customer_profile)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class GetOrderByClientSecretView(views.APIView):
    @csrf_exempt  # Use this decorator if CSRF protection is enabled
    def post(self, request, *args, **kwargs):
        print(request.body)
        payment_intent_id = request.data.get('payment_intent_id')  # Assuming client_secret is sent in the request data

        if payment_intent_id:
            try:
                order = Order.objects.get(payment_intent_id=payment_intent_id)
                serializer = OrderSerializer(order)  # Use your serializer to serialize the order data
                return JsonResponse(serializer.data)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found'}, status=404)
        else:
            return JsonResponse({'error': 'Client secret not provided'}, status=400)


class DeliveryDetailsListCreateView(generics.ListCreateAPIView):
    queryset = DeliveryDetails.objects.all()
    serializer_class = DeliveryDetailsSerializer


class OrderInvoiceListCreateView(generics.ListCreateAPIView):
    queryset = OrderInvoice.objects.all()
    serializer_class = OrderInvoiceSerializer

class PaymentIntentCreateView(View):

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        if not order_id:
            return JsonResponse({'error': 'Order ID not provided'}, status=400)
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  
        try:
            order = Order.objects.get(id=order_id)

            cart = order.cart
            if not cart:
                return JsonResponse({'error': 'Cart not found'}, status=404)
            cart_total_price = cart.total_price  # Fetch the total price from the related Cart


            intent = stripe.PaymentIntent.create(
                amount=int(cart_total_price * 100),  # Convert to cents (Stripe uses cents)
                currency='usd',
                automatic_payment_methods={
                'enabled': True,  # Set to True to enable automatic payment methods that require redirects
            },
                metadata={'order_id': str(order_id)},  # Metadata for tracking
            )

            #Update the order's payment_intent_id field with the PaymentIntent ID
            
            order.payment_intent_id = intent.id
            client_secret = intent.client_secret
            order.payment_intent_secret = client_secret
            order.save()

            
            return JsonResponse({'clientSecret': client_secret})

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

@csrf_exempt
def stripe_webhook(request):
    # Retrieve the webhook event data from the request
    payload = request.body
    sig_header = request.headers['Stripe-Signature']
    endpoint_secret = 'whsec_238d40800eaba7cfea949b206171b2019d1e1e3677463dc17b5bd05abd60391a'

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event based on its type
    print(event['type'])
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # Retrieve the payment intent object
        order_id = payment_intent['metadata']['order_id']  # Extract order ID from metadata
        try:
            order = Order.objects.get(pk=order_id)
            # Update order status or any other relevant details
            order.payment_order_status = 'paid'
            order.order_status = 'confirmed'
            order.save()
            order.cart.delete()

            send_order_placed_email(order.customer.email, order_id)

            return JsonResponse({'message': 'Order updated successfully'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Handle other event types if needed

    return JsonResponse({'message': 'Webhook received'})



class CheckCartOrderView(View):

    '''

    This view will check if this order have a cart : if True then get the order details

    '''
    authintication_classes = [IsAuthenticated, IsCustomer]  # Disable authentication classes
    def get(self, request):
        cart_id = request.GET.get('cart_id')  # Assuming the cart ID is passed as a query parameter
        if not cart_id:
            return JsonResponse({'error': 'Cart ID not provided'}, status=400)

        try:
            order = Order.objects.get(cart_id=cart_id)  # Assuming cart_id is a foreign key in the Order model
            # If an order exists for this cart, return the order details
            order_data = {
                
                'order_id': order.id,
                'order_status': order.order_status,
                'notes': order.notes,
                'payment_way': order.payment_way,
                'order_mode': order.order_mode,
                'selected_order_time': order.selected_order_time.isoformat() if order.selected_order_time else None,
                'coupon_code': order.coupon_code,
                'total_price': str(order.total_price),
                'customer': order.customer.id,
                'cart': order.cart.id,
                'delivery_details': {
                    'id': order.delivery_details.id,
                    'full_name': order.delivery_details.full_name,
                    'phone': order.delivery_details.phone,
                    'email': order.delivery_details.email,
                    'post_code': order.delivery_details.post_code,
                    'city': order.delivery_details.city,
                    'area': order.delivery_details.area,
                    'lane': order.delivery_details.lane,
                    'street_name': order.delivery_details.street_name,
                    'house_number': order.delivery_details.house_number,
                    'floor': order.delivery_details.floor,
                    'company_name': order.delivery_details.company_name,
                },
                'cart_has_order': True,
            }
            return JsonResponse(order_data)
        except Order.DoesNotExist:
            # If no order exists, indicate that it's allowed to create a new order with this cart
            return JsonResponse({'cart_has_order': False,'message': 'No order found for this cart. You can create a new order.'})
        

class OrderPatchUpdateView(views.APIView):
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderPagination(PageNumberPagination):
    page_size = 2  # Set the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Optional: set the maximum page size

    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'num_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data,
        })

class AdminListRestaurantOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    pagination_class = OrderPagination  # Use the custom pagination class
    permission_classes = [IsAuthenticated, IsAdminOfRestaurant]

    def get_queryset(self):
        admin = self.request.user.admin_profile
        restaurant = admin.restaurant
        order_status = self.request.query_params.get('order_status')  # Get the order_status filter from query params
        order_mode = self.request.query_params.get('order_mode')

        queryset = Order.objects.filter(restaurant=restaurant)

        if order_status:
            queryset = queryset.filter(order_status=order_status)
        
        if order_mode:
            queryset = queryset.filter(order_mode=order_mode)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)  # Paginate the queryset
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    





class ListCustomerOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve orders associated with the current authenticated user (assuming customer is the user)
        return Order.objects.filter(customer=self.request.user.customer_profile)
    


def refund_payment(payment_intent_id, amount):
    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            # amount=amount,  # Specify the amount to refund
        )
        return refund
    except stripe.error.StripeError as e:
        return str(e)
    

class ChangeOrderStatusView(APIView):
    def refund_and_send_email(self, order, new_status, customer_email):
        if order.payment_intent_id:
            refund_result = refund_payment(order.payment_intent_id, int(order.total_price))
            if refund_result:
                send_order_status_changed_email(customer_email, order.id, new_status)
                return JsonResponse({'message': f'Order canceled and payment refunded successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Failed to refund payment'}, status=500)
        else:
            return JsonResponse({'error': 'No payment intent ID found'}, status=400)

    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        new_status = request.data.get('new_status')

        if not order_id:
            return JsonResponse({'error': 'Order ID not provided'}, status=400)
        
        try:
            order = Order.objects.get(id=order_id)
            customer = order.customer
            customer_email = customer.email
            order_mode = order.order_mode
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        
        if order_mode == 'delivery':
            # Check if the new status is valid
            valid_statuses = ['confirmed', 'in_progress', 'on_the_way', 'delivered', 'canceled']
            if new_status not in valid_statuses:
                return JsonResponse({'error': 'Invalid status provided'}, status=400)
            
            # Check if the order status allows changing to 'canceled'
            if new_status == 'canceled':
                order.order_status = new_status
                order.save()
                return self.refund_and_send_email(order, new_status, customer_email)

            # Update order status for other statuses
            order.order_status = new_status
            order.save()

        elif order_mode == 'pick_up':
            # Check if the new status is valid
            valid_statuses = ['confirmed', 'in_progress', 'canceled']
            if new_status not in valid_statuses:
                return JsonResponse({'error': 'Invalid status provided'}, status=400)
            
            # Check if the order status allows changing to 'canceled'
            if new_status == 'canceled':
                order.order_status = new_status
                order.save()
                return self.refund_and_send_email(order, new_status, customer_email)

            # Update order status for other statuses
            order.order_status = new_status
            order.save()

        # Send email for status change if not canceled
        send_order_status_changed_email(customer_email, order_id, new_status)
        return JsonResponse({'message': f'Order status updated to {new_status}'}, status=200)


# class SSEOrdersUpdateView(View):
#     def get(self, request, *args, **kwargs):
#         response = HttpResponse(content_type='text/event-stream')
#         response['Cache-Control'] = 'no-cache'
#         response['Connection'] = 'keep-alive'

#         def event_stream():
#             while True:
#                 # Check for new orders (this is just an example, replace with actual logic)
#                 new_orders = check_for_new_orders()

#                 if new_orders:
#                     # Send SSE event for each new order
#                     for order in new_orders:
#                         yield f"data: {order}\n\n"
#                 else:
#                     # Send a keep-alive message to prevent connection timeout
#                     yield ":\n\n"

#                 # Sleep for a while before checking again
#                 time.sleep(5)

#         return HttpResponse(event_stream(), content_type='text/event-stream')
    

from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.functional import SimpleLazyObject
import json
class SSEView(View):
    permission_classes = [IsAuthenticated]

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Extract token from query parameters
        user_token = request.GET.get('token')
        
        # Authenticate the user based on the token
        user = User.objects.filter(auth_token=user_token).first()
        print (user.username)
        if not user:
            return HttpResponse(status=401)

        # Your SSE logic here
        response = HttpResponse(content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        # response['Connection'] = 'keep-alive'

        def send_event(event_data):
            response.write(f"data: {json.dumps(event_data)}\n\n")

        def new_order_created(sender, instance, created, **kwargs):
            if created and instance.restaurant == user.admin_profile.restaurant:
                send_event({'message': 'New order created'})

        # Connect the signal to the function
        post_save.connect(new_order_created, sender=Order)

        return response