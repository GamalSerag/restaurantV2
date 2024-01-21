from django.db import models
from customer_app.models import Customer
from restaurant_app.models import Category, Restaurant, MenuItem

class Cart(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    
    service = models.CharField(max_length=255)
    cart_items = models.ManyToManyField('CartMenuItem', related_name='carts')

    def __str__(self):
        return f"Cart #{self.pk} - {self.customer.first_name} {self.customer.last_name}"

class CartMenuItem(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)
    saus = models.JSONField(null=True, blank=True)
    size = models.JSONField(null=True, blank=True)
    categories = models.ManyToManyField(Category)
    def __str__(self):
        return f"CartMenuItem #{self.pk} - {self.menu_item.name} - Quantity: {self.quantity}"
