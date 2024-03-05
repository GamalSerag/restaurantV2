from django.urls import path
from customer_app.views import AddFavoriteRestaurantView, CustomerViewSet, FavoriteRestaurantListView

urlpatterns = [
    path('customers/', CustomerViewSet.as_view(), name='customer-registration'),

    path('add-favorites/', AddFavoriteRestaurantView.as_view(), name='add-favorite_restaurant'),
    path('favorite-restaurants/', FavoriteRestaurantListView.as_view(), name='favorite_restaurants'),
]