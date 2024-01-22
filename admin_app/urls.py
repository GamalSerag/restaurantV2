from django.urls import path
from .views import AdminViewSet

urlpatterns = [
    path('admins/', AdminViewSet.as_view({'get': 'list'}), name='admin-list'),
    
]