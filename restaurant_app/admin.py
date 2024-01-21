from django.contrib import admin

from .models import Category, MenuItem, OrderMode, Restaurant,RestaurantTable, RestaurantRegion, MenuSection

admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(OrderMode)
admin.site.register(MenuItem)
admin.site.register(RestaurantTable)
admin.site.register(MenuSection)
admin.site.register(RestaurantRegion)
