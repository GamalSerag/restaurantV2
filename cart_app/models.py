from django.http import Http404
from django.utils import timezone
from decimal import Decimal
from django.db import models
from cart_app.utils import calculate_cart_item_total_prices
from customer_app.models import Customer
from restaurant_app.models import Category, MenuItemExtraItem, MenuItemTypeItem, Restaurant, MenuItem
from django.contrib import admin
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist




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


    def calculate_total_price(self):
        # Check if the Cart instance has a primary key (i.e., if it's saved)
        if self.pk:
            total_price_after_discount = self.items.aggregate(total=Sum('total_price_after_discount'))['total']
            if total_price_after_discount is None:
                total_price_after_discount = 0
            if self.order_mode == 'delivery' and self.restaurant:
                total_price_after_discount += self.delivery_fee
            return total_price_after_discount
        else:
            # Cart instance is not saved yet, return 0 or any default value
            return 0
    

    def save(self, *args, **kwargs):
        # If the cart is being created for the first time
        if not self.pk:
            # Get the delivery fee from the associated restaurant
            if self.order_mode == 'delivery' and self.restaurant:
                self.delivery_fee = self.restaurant.delivery_fee
            else:
                self.delivery_fee = 0  # Set delivery fee to 0 for other order modes or when restaurant is not set
        self.total_price = self.calculate_total_price()
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
    
    def save(self, *args, **kwargs):
        if not self.pk:
            base_price, total_price_with_quantity, total_price_without_quantity = calculate_cart_item_total_prices(
                self.menu_item, self.selected_type_ids, self.selected_extra_ids, self.quantity
            )

            self.price = base_price
            self.total_price_before_discount = total_price_with_quantity
            self.total_price_after_discount = total_price_without_quantity

        super().save(*args, **kwargs)

    def __str__(self):
        return f"CartItem #{self.pk}"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('get_cart_title', 'total_price', 'customer', 'restaurant', 'order_mode')

    def get_cart_title(self, obj):
        return f"Cart #{obj.pk} "
    get_cart_title.short_description = 'Title'

    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('get_cart_item_title', 'quantity', 'total_price_before_discount', 'total_price_after_discount', 'price', 'cart', 'get_restaurant_name')

    def get_cart_item_title(self, obj):
        return f"CartItem #{obj.pk} - {obj.menu_item.name} - {obj.cart.restaurant.name} - Quantity: {obj.quantity} - {obj.cart.customer.first_name} {obj.cart.customer.last_name}"

    def get_restaurant_name(self, obj):
        return obj.cart.restaurant.name

    get_cart_item_title.short_description = 'Title'