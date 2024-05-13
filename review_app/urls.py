from django.urls import path
from .views import CombinedRatingView, RestaurantRatingsView

urlpatterns = [
    path('rate/', CombinedRatingView.as_view(), name='rate-restaurant'),
    path('get-restaurant-rating/', CombinedRatingView.as_view(), name='get-restaurant-rating'),
    path("get-restaurant-ratings/<int:restaurant_id>/", RestaurantRatingsView.as_view(), name="get-restaurant-ratings"),
]