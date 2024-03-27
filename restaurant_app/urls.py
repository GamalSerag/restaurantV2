from django.urls import path
from .views import AdminRestaurantDetailView, CategoriesUpdateView, CategoriesView, CategoryAdminRequestRejectView, CategoryAdminRequestView, CategoryApprovalView, MenuItemCreateView, MenuItemDetailView, MenuItemExtraDeleteView, MenuItemExtraItemDeleteView, MenuItemTypeDeleteView, MenuItemTypeItemDeleteView, MenuItemUpdateView, RestaurantCategoryDeleteView, RestaurantCategoryListCreateView, RestaurantCategoryUpdateView,RestaurantListViewByCity, RestaurantListView, RestaurantDetailView, CityCategoriesView
urlpatterns = [
    
    path('', RestaurantListView.as_view()),
    path('edit/<int:pk>/', AdminRestaurantDetailView.as_view(), name='restaurant-detail'),
    path('<int:pk>/', RestaurantDetailView.as_view()),
    path('admin/<int:pk>/', AdminRestaurantDetailView.as_view()),
    
    path('categories/add/', CategoriesView.as_view()),
    path('categories/create-request/', CategoryAdminRequestView.as_view(), name='create-request'),
    path('categories/admin-requests/', CategoryAdminRequestView.as_view(), name='categories-admin-requests'),
    path('categories/approve-request/<int:pk>/', CategoryApprovalView.as_view(), name='superadmin-approve-categories-request'),
    path('categories/reject-request/<int:pk>/', CategoryAdminRequestRejectView.as_view(), name='superadmin-reject-categories-request'),
    path('categories/edit/<int:pk>/', CategoriesUpdateView.as_view()),
    path('categories/<str:city_name>/', CityCategoriesView.as_view()),
    path('categories/', CategoriesView.as_view()),
    

    path('r-categories/add/', RestaurantCategoryListCreateView.as_view()),
    path('r-categories/edit/<int:pk>/', RestaurantCategoryUpdateView.as_view()),
    path('r-categories/delete/<int:pk>/', RestaurantCategoryDeleteView.as_view()),
    path('r-categories/', RestaurantCategoryListCreateView.as_view()),
    
    
    path('<str:city_name>/', RestaurantListViewByCity.as_view()),
    
    path('menu-item/<int:pk>/', MenuItemDetailView.as_view(), name='menuitem-detail'),

    path('menu-item/add/', MenuItemCreateView.as_view(), name='menuitem-create'),
    path('menu-item/delete/<int:pk>/', MenuItemUpdateView.as_view(), name='menuitem-delete'),
    path('menu-item/edit/<int:pk>/', MenuItemUpdateView.as_view(), name='menuitem-edit'),
    
    path('menu-item-extra/delete/<int:pk>/', MenuItemExtraDeleteView.as_view(), name='menuitem-extra-delete'),
    path('menu-item-extra-item/delete/<int:pk>/', MenuItemExtraItemDeleteView.as_view(), name='menuitem-extra-item-delete'),

    path('menu-item-type/delete/<int:pk>/', MenuItemTypeDeleteView.as_view(), name='menuitem-extra-delete'),
    path('menu-item-type-item/delete/<int:pk>/', MenuItemTypeItemDeleteView.as_view(), name='menuitem-extra-item-delete'),


]
