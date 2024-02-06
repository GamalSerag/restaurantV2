import json
from django.db import models
from location_app.models import City, Country
from django.contrib.postgres.fields import ArrayField
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
    timestamps = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to=restaurant_logo_path, null=True)
    background = models.ImageField(upload_to=restaurant_background_path, null=True)
    state = models.BooleanField(default='True')  # open or closed
    free_delivery = models.CharField(max_length=10, null=True)
    categories = models.ManyToManyField('Category', blank=True)
    address = models.TextField(max_length=500)
    open_in = models.CharField(max_length=5, null=True)
    close_in = models.CharField(max_length=5, null=True)
    order_modes = models.ManyToManyField('OrderMode', blank=True)
    # additions = models.JSONField() ###     ######     #####     #######    #########    ####
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



class OrderMode(models.Model):
   
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to=menuitem_image_path, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=None)
    ingredients = ArrayField(models.CharField(max_length=100, null=True, blank=True), default=list)
    sizes_and_prices = ArrayField(models.JSONField(), default=list)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

    


class RestaurantTable(models.Model): # table in the restaurant 
    timestamps = models.DateTimeField(auto_now_add=True)
    table_number = models.IntegerField()
    size = models.IntegerField()
    table_status = models.BooleanField()
    # region = models.ForeignKey('RestaurantRegion', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Table {self.table_number} - {self.restaurant.name}"



class MenuSection(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class RestaurantRegion(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name