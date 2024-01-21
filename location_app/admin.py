from django.contrib import admin

from .models import City, Country

admin.site.register(Country)
admin.site.register(City)
