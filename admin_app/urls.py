from django.urls import path
from .views import AdminView

urlpatterns = [
    path('<int:pk>/', AdminView.as_view(), name='admin-details'),
    
]