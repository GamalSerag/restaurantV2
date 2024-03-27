from decimal import Decimal
from django.db import models
from customer_app.models import Customer
from restaurant_app.models import MenuItemExtraItem, MenuItemTypeItem, Restaurant, MenuItem, Category, RestaurantTable
from cart_app.models import Cart
# from payment_app.models import PaymentWay
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
import json

# from delivery_app.models import DeliveryMan

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('card', _('Credit/Debit Card')),
        ('cash', _('Cash on Delivery')),
        ('paypal', _('PayPal')),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    order_mode = models.CharField(max_length=20)
    order_status = models.CharField(max_length=255, default='pending')
    notes = models.TextField(blank=True, null=True)
    # delivery_man = models.ForeignKey('delivery_app.DeliveryMan', on_delete=models.CASCADE)
    payment_way = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    delivery_or_pickup_time = models.DateTimeField(null=True, blank=True, help_text="Specify the time for delivery or pickup based on the order mode.")
    coupon_code = models.CharField(max_length=255, blank=True, null=True)
    delivery_details = models.OneToOneField('DeliveryDetails', on_delete=models.CASCADE, related_name='orders')
    items = models.JSONField(null=True, blank=True, encoder=DecimalEncoder)  # JSONField to store cart items as JSON
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Total price field
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        # If the order is being created for the first time
        if not self.pk and self.cart:
            # Get all items from the cart as a list of dictionaries
            cart_items = list(self.cart.items.values())
            for item in cart_items:
                item['created_at'] = item['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                extra_ids = item.get('selected_extra_ids', [])
                type_ids = item.get('selected_type_ids', [])
                
                # Update selected_extra_ids with names and prices of ExtraItems
                extra_items = MenuItemExtraItem.objects.filter(id__in=extra_ids)
                extra_names_prices = [{'name': extra.name, 'price': extra.price} for extra in extra_items]
                item['selected_extra_ids'] = extra_names_prices
                
                # Update selected_type_ids with names and prices of TypeItems
                type_items = MenuItemTypeItem.objects.filter(id__in=type_ids)
                type_names_prices = [{'name': type_item.name, 'price': type_item.price} for type_item in type_items]
                item['selected_type_ids'] = type_names_prices

            self.items = cart_items
            # Calculate the total price based on cart items
            self.total_price = sum(item['total_price_after_discount'] for item in cart_items) 
            self.order_mode = self.cart.order_mode

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.first_name} {self.customer.last_name}"




class DeliveryDetails(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    post_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    lane = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    house_number = models.CharField(max_length=255, blank=True, null=True)
    floor = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):
        return f"DeliveryAddress #{self.pk} - {self.full_name}"




class OrderInvoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2)
    restaurant_vat = models.DecimalField(max_digits=5, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"OrderInvoice #{self.pk} - Order #{self.order.pk}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant_table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reservation #{self.pk} - {self.customer.first_name} {self.customer.last_name}"

