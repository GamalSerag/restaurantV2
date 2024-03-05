from django.db import models
from customer_app.models import Customer
from restaurant_app.models import Category, Restaurant, MenuItem
from django.contrib import admin



class Cart(models.Model):

    order_mode_choices = [
        ('delivery', 'Delivery'),
        ('pick_up', 'Pick Up'),
        ('dine_in', 'Dine In')
    ] 

    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order_mode = models.CharField(max_length=20, choices=order_mode_choices, default='delivery')
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # If the cart is being created for the first time
        if not self.pk:
            # Get the delivery fee from the associated restaurant
            if self.order_mode == 'delivery' and self.restaurant:
                self.delivery_fee = self.restaurant.delivery_fee
            else:
                self.delivery_fee = 0  # Set delivery fee to 0 for other order modes or when restaurant is not set
        
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Cart #{self.pk}"
    
    class Meta:
        # Ensure that the combination of customer and restaurant is unique together
        unique_together = ['customer', 'restaurant']

class CartItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_after_discount = models.DecimalField(max_digits=8, decimal_places=2)
    total_price_before_discount = models.DecimalField(max_digits=8, decimal_places=2)
    total_price_after_discount = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    selected_extra_ids = models.JSONField(blank=True, null=True)  # Store selected_extra_ids as JSON
    selected_type_ids = models.JSONField(blank=True, null=True)  # Store selected_type_ids as JSON
    
    def __str__(self):
        return f"CartItem #{self.pk}"
    

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('get_cart_title', 'total_price', 'customer', 'restaurant', 'order_mode')
    
    def get_cart_title(self, obj):
        return f"Cart #{obj.pk} "
    get_cart_title.short_description = 'Title'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('get_cart_item_title', 'quantity', 'total_price_before_discount', 'total_price_after_discount', 'price', 'cart', 'get_restaurant_name')
    
    def get_cart_item_title(self, obj):
        return f"CartItem #{obj.pk} - {obj.menu_item.name} - {obj.cart.restaurant.name} - Quantity: {obj.quantity} - {obj.cart.customer.first_name} {obj.cart.customer.last_name}"
    
    def get_restaurant_name(self, obj):
        return obj.cart.restaurant.name
    
    get_cart_item_title.short_description = 'Title'