from django.urls import path
from .views import MenuItemDetailView,RestaurantListViewByCity, RestaurantListView, RestaurantDetailView, CityCategoriesView
urlpatterns = [
    
    path('', RestaurantListView.as_view()),
    path('edit/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('<int:pk>/', RestaurantDetailView.as_view()),
    path('<str:city_name>/', RestaurantListViewByCity.as_view()),
    path('<str:city_name>/categories', CityCategoriesView.as_view()),
    path('menuitem/<int:pk>/', MenuItemDetailView.as_view(), name='menuitem-detail')
]
