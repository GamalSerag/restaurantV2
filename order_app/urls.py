from django.urls import path

from .views import AdminListRestaurantOrdersView, ChangeOrderStatusView, CheckCartOrderView, GetOrderByClientSecretView, ListCustomerOrdersAPIView, OrderDetailView, OrderListCreateView, OrderPatchUpdateView, OrderStatusCountAPIView, PaymentIntentCreateView, download_pdf, stripe_webhook, textshare, upload_file
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create/', OrderListCreateView.as_view(), name='order-create'),

    path('<int:pk>/', OrderDetailView.as_view(), name='order-details'),
    path('get-by-payment-intent-id/', csrf_exempt(GetOrderByClientSecretView.as_view()), name='get_order_by_client_secret'),
    path('customer-orders/', ListCustomerOrdersAPIView.as_view(), name='customer-orders'),

    path('get-restaurant-orders/', AdminListRestaurantOrdersView.as_view(), name='get_restaurant_orders'),

    path('create-payment-intent/', csrf_exempt(PaymentIntentCreateView.as_view()), name='create_payment_intent'),
    path('stripe-webhook/', csrf_exempt(stripe_webhook), name='stripe_webhook'),

    path('download-pdf/', download_pdf, name='download_pdf'),
    path('upload/', upload_file, name='upload_file'),

    path('check-cart-order/', CheckCartOrderView.as_view(), name='check-cart-order'),
    path('update/<int:pk>/', OrderPatchUpdateView.as_view(), name='order-update'),
    path('change-order-status/<int:order_id>/', csrf_exempt(ChangeOrderStatusView.as_view()), name='change-order-status'),
    # path('sse/', SSEView.as_view(), name='sse'),
    path('get-count/', OrderStatusCountAPIView.as_view(), name='get_count'),
    path('text-share/', textshare, name='text-share')
]