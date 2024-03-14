from django.contrib import admin
from .models import Category, MenuItem, MenuItemExtra, MenuItemExtraItem, MenuItemType, MenuItemTypeItem, Restaurant, RestaurantTable, RestaurantRegion, MenuSection, RestaurantCategory, SizeAndPrice

# Define Inline Admin for SizeAndPrice
class SizeAndPriceInline(admin.TabularInline):
    model = SizeAndPrice
    extra = 0

# Define custom admin class for MenuItem
class MenuItemAdmin(admin.ModelAdmin):
    inlines = [SizeAndPriceInline]  # Include SizeAndPriceInline in the admin interface for MenuItem

# Register models with custom admin classes
admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(MenuItem, MenuItemAdmin)  # Register MenuItem with custom admin class
admin.site.register(RestaurantTable)
admin.site.register(MenuSection)
admin.site.register(RestaurantRegion)
admin.site.register(RestaurantCategory)

admin.site.register(MenuItemExtraItem)
admin.site.register(MenuItemExtra)

admin.site.register(MenuItemTypeItem)
admin.site.register(MenuItemType)
admin.site.register(SizeAndPrice)