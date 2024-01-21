from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from .serializers import CountrySerializer, CitySerializer 
from .models import Country, City


class CountryView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityView(generics.RetrieveAPIView, generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get(self, request, *args, **kwargs):
        # Check if 'country_name' is present in kwargs
        if 'country_name' in kwargs:
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        # Retrieve the country name from the URL parameter
        country_name = self.kwargs.get('country_name')
        
        # Check if 'country_name' is present in kwargs
        if country_name:
            # Get the country object or return a 404 response if not found
            country = get_object_or_404(Country, name=country_name)
            # Filter the queryset based on the country
            return City.objects.filter(country=country)
        else:
            # Return the default queryset (all cities) for single city retrieval
            return super().get_queryset()




