from django.urls import path
from .views import CartCreateView, CartDetailsView, CartItemCreateView, CartItemDeleteView, CartItemRetieveView, CartItemUpdateView, CartUpdateView

urlpatterns = [
    path('create-cart/', CartCreateView.as_view(), name='create_cart'),
    path('create-cart-item/', CartItemCreateView.as_view(), name='create_cart_item'),
    path('get-cart/', CartDetailsView.as_view(), name='get_cart_item'),

    path('cart-item/update/<int:pk>/', CartItemUpdateView.as_view(), name='update_cart_item'),
    path('cart-item/delete/<int:pk>/', CartItemDeleteView.as_view(), name='delete_cart_item'),
    path('get-cart-item/<int:pk>/', CartItemRetieveView.as_view(), name='delete_cart_item'),

    path('update/<int:pk>/', CartUpdateView.as_view(), name='update_cart_details'),
]