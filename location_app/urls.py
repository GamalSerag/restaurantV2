from django.urls import path
from .views import CityView, CountryView
urlpatterns = [
    
    path('countries/', CountryView.as_view()),
    path('cities/<int:pk>/', CityView.as_view()),
    path('cities/<str:country_name>/', CityView.as_view(), name='city-list'),
]
