from django.urls import path
from .views import CartCreateView, CartItemCreateView

urlpatterns = [
    path('create-cart/', CartCreateView.as_view(), name='create_cart'),
    path('create-cart-item/', CartItemCreateView.as_view(), name='create_cart_item'),
]