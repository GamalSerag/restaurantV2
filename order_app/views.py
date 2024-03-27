from django.conf import settings
from rest_framework import generics, views

from django.http import JsonResponse
from django.views import View
# from djstripe.models import PaymentIntent
from stripe import PaymentIntent
import stripe
from rest_framework import serializers, status
from rest_framework.response import Response

from cart_app.models import Cart
from order_app.serializers import DeliveryDetailsSerializer, OrderInvoiceSerializer, OrderSerializer
from .models import DeliveryDetails, Order, OrderInvoice
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ErrorDetail
from django.http import FileResponse
from  rest_framework.permissions import IsAuthenticated
# from django_cron import CronJobBase, Schedule

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
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY  # Or use your live secret key for production
        try:
            order = Order.objects.get(id=order_id)
            cart_total_price = order.cart.total_price  # Fetch the total price from the related Cart
            

            intent = stripe.PaymentIntent.create(
                amount=int(cart_total_price * 100),  # Convert to cents (Stripe uses cents)
                currency='usd',  # Adjust the currency as needed
                # confirm=True,  # Confirm the PaymentIntent immediately
                # payment_method_types=['card'],
                automatic_payment_methods={
                'enabled': True,  # Set to True to enable automatic payment methods that require redirects
                # 'allow_redirects': 'never',  # Allow redirects for supported payment methods
            },
                metadata={'order_id': str(order_id)},  # Metadata for tracking
                # return_url='http://192.168.1.37:8200/restaurant'
            )

            # Update the order's payment_intent_id field with the PaymentIntent ID
            order.payment_intent_id = intent.id
            order.save()

            client_secret = intent.client_secret
            return JsonResponse({'clientSecret': client_secret})

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

@csrf_exempt
def stripe_webhook(request):
    # print(request.body)
    # Retrieve the webhook event data from the request
    payload = request.body
    sig_header = request.headers['Stripe-Signature']
    endpoint_secret = 'whsec_238d40800eaba7cfea949b206171b2019d1e1e3677463dc17b5bd05abd60391a'  # Replace with your actual webhook secret

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
            order.order_status = 'paid'
            # order.cart = None
            order.save()
            order.cart.delete()
            return JsonResponse({'message': 'Order updated successfully'})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Handle other event types if needed

    return JsonResponse({'message': 'Webhook received'})



class CheckCartOrderView(View):
    authintication_classes = [IsAuthenticated]  # Disable authentication classes
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
                'delivery_or_pickup_time': order.delivery_or_pickup_time.isoformat() if order.delivery_or_pickup_time else None,
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