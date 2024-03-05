from django.urls import path
from .views import AdminRestaurantDetailView, CategoriesView, MenuItemCreateView, MenuItemDetailView, MenuItemUpdateView, RestaurantCategoryDeleteView, RestaurantCategoryListCreateView, RestaurantCategoryUpdateView,RestaurantListViewByCity, RestaurantListView, RestaurantDetailView, CityCategoriesView
urlpatterns = [
    
    path('', RestaurantListView.as_view()),
    path('edit/<int:pk>/', AdminRestaurantDetailView.as_view(), name='restaurant-detail'),
    path('<int:pk>/', RestaurantDetailView.as_view()),
    path('admin/<int:pk>/', AdminRestaurantDetailView.as_view()),
    
    path('categories/add/', CategoriesView.as_view()),
    path('categories/<str:city_name>/', CityCategoriesView.as_view()),
    path('categories/', CategoriesView.as_view()),

    path('r-categories/add/', RestaurantCategoryListCreateView.as_view()),
    path('r-categories/edit/<int:pk>/', RestaurantCategoryUpdateView.as_view()),
    path('r-categories/delete/<int:pk>/', RestaurantCategoryDeleteView.as_view()),
    path('r-categories/', RestaurantCategoryListCreateView.as_view()),
    
    path('<str:city_name>/', RestaurantListViewByCity.as_view()),
    
    path('menu-item/<int:pk>/', MenuItemDetailView.as_view(), name='menuitem-detail'),

    path('menu-item/add/', MenuItemCreateView.as_view(), name='menuitem-create'),
    path('menu-item/delete/<int:pk>/', MenuItemUpdateView.as_view(), name='menuitem-create'),
    path('menu-item/edit/<int:pk>/', MenuItemUpdateView.as_view(), name='menuitem-create'),
]
