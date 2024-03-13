import json
from django.db import models
from location_app.models import City, Country
from django.contrib.postgres.fields import ArrayField
from multiselectfield import MultiSelectField

from offers_app.models import Offer
from django.contrib import admin
# from django_jsonform.models.fields import ArrayField, JSONField



def restaurant_logo_path(instance, filename):
    # This function will be used to generate the upload path
        return f'resuarant/logo{instance.name}/{filename}'

def restaurant_background_path(instance, filename):
    # This function will be used to generate the upload path
        return f'resuarant/background{instance.name}/{filename}'

def category_image_path(instance, filename):
    # This function will be used to generate the upload path
    return f'category/{instance.name}/{filename}'

def menuitem_image_path(instance, filename):
    # This function will be used to generate the upload path
    return f'menuitems/{instance.name}/{filename}'




class Restaurant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=restaurant_logo_path, null=True)
    background = models.ImageField(upload_to=restaurant_background_path, null=True)
    state = models.BooleanField(default='True')  # open or closed
    free_delivery = models.CharField(max_length=10, null=True)
   
    open_in = models.CharField(max_length=5, null=True)
    close_in = models.CharField(max_length=5, null=True)
    address = models.TextField(max_length=500)
    order_modes = models.JSONField(default=list)
    
    tax = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    minimum_order = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    delivery_time = models.IntegerField(null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15 , null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=category_image_path)

    def __str__(self):
        return self.name
    

class RestaurantCategory(models.Model):
    name = models.CharField(max_length=50)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    offer = models.OneToOneField(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    tax =  models.FloatField(null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('restaurant', 'category')

    def __str__(self):
        return f"{self.name} (({self.category.name})) - R:{self.restaurant.name}"
    

class SizeAndPrice(models.Model):
    size = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.size} - ${self.price}"



class MenuItemExtra(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id}-{self.title}"

class MenuItemExtraItem(models.Model):
    extra = models.ForeignKey(MenuItemExtra, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.id} - {self.name}"
    

class MenuItemType(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id}-{self.title}"

class MenuItemTypeItem(models.Model):
    type = models.ForeignKey(MenuItemType, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}"


class MenuItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=250)
    image = models.ImageField(upload_to=menuitem_image_path, null=True)
    category = models.ForeignKey(RestaurantCategory, on_delete=models.CASCADE, related_name='menu_items', default=None, null=True)
    ingredients = ArrayField(models.CharField(max_length=100, null=True, blank=True), default=list, null = True)
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    offer = models.OneToOneField(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    extras = models.ManyToManyField(MenuItemExtra, blank=True)
    types = models.ManyToManyField(MenuItemType, blank=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
    def get_sizes_and_prices_display(self):
        sizes_and_prices = SizeAndPrice.objects.filter(menu_item=self)
        return ", ".join([f"{size.size} - ${size.price}" for size in sizes_and_prices])
    
    


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'get_sizes_and_prices_display', 'category', 'restaurant']




class RestaurantTable(models.Model): # table in the restaurant 
    created_at = models.DateTimeField(auto_now_add=True)
    table_number = models.IntegerField()
    size = models.IntegerField()
    table_status = models.BooleanField()
    # region = models.ForeignKey('RestaurantRegion', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Table {self.table_number} - {self.restaurant.name}"



class MenuSection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class RestaurantRegion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name