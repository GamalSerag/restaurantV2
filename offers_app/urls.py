from django.urls import path
from .views import OfferDeleteView, OfferUpdateView, create_offer_and_associate

urlpatterns = [
    
    path('add/', create_offer_and_associate, name='add offer'),
    path('delete/<int:pk>/', OfferDeleteView.as_view(), name='delete offer'),
    path('edit/<int:pk>/', OfferUpdateView.as_view(), name='edit offer'),
    
]