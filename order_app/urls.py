from django.urls import path

from .views import CheckCartOrderView, OrderDetailView, OrderListCreateView, OrderPatchUpdateView, PaymentIntentCreateView, download_pdf, stripe_webhook
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create/', OrderListCreateView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-details'),
    path('create-payment-intent/', csrf_exempt(PaymentIntentCreateView.as_view()), name='create_payment_intent'),
    path('stripe-webhook/', csrf_exempt(stripe_webhook), name='stripe_webhook'),
    path('download-pdf/', download_pdf, name='download_pdf'),
    path('check-cart-order/', CheckCartOrderView.as_view(), name='check-cart-order'),
    path('update/<int:pk>/', OrderPatchUpdateView.as_view(), name='order-update'),
]