from django.urls import path
from customer_app.views import AddFavoriteRestaurantView, CustomerViewSet, FavoriteRestaurantListView

urlpatterns = [
    path('get-customer/', CustomerViewSet.as_view(), name='customer-details'),

    path('add-favorites/', AddFavoriteRestaurantView.as_view(), name='add-favorite_restaurant'),
    path('favorite-restaurants/', FavoriteRestaurantListView.as_view(), name='favorite_restaurants'),
]