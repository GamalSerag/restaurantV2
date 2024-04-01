from datetime import timedelta
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

    ORDER_STATUS_CHOICES = (
        ('pinding', _('Pinding')),
        ('confirmed', _('Confirmed')),
        ('in_progress', _('In Progress')),
        ('on_the_way', _('On The Way')),
        ('delivered', _('Delivered')),
        ('canceled', _('Canceled')),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    order_mode = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    # delivery_man = models.ForeignKey('delivery_app.DeliveryMan', on_delete=models.CASCADE)
    payment_way = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    order_status = models.CharField(max_length=255, default='pinding', choices=ORDER_STATUS_CHOICES)
    time_left = models.DurationField(blank=True, null=True, default=timedelta(minutes=20), help_text="Countdown time until order delivery")
    selected_order_time = models.DateTimeField(null=True, blank=True, help_text="Specify the time for delivery or pickup based on the order mode.")
    coupon_code = models.CharField(max_length=255, blank=True, null=True)
    delivery_details = models.OneToOneField('DeliveryDetails', on_delete=models.CASCADE, related_name='orders')
    items = models.JSONField(null=True, blank=True, encoder=DecimalEncoder)  # JSONField to store cart items as JSON
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Total price field
    payment_order_status = models.CharField(max_length=255, default='pending')
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    payment_intent_secret = models.CharField(max_length=255, blank=True, null=True)
    
    
    def update_from_cart(self):
        cart_items = list(self.cart.items.values())
        for item in cart_items:
            item['created_at'] = item['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            extra_ids = item.get('selected_extra_ids', [])
            type_ids = item.get('selected_type_ids', [])
            
            # Rename selected_extra_ids to selected_extra_items
            item['selected_extra_items'] = item.pop('selected_extra_ids', [])

            # Rename selected_type_ids to selected_type_items
            item['selected_type_items'] = item.pop('selected_type_ids', [])

            # Update selected_extra_items with names and prices of ExtraItems
            extra_items = MenuItemExtraItem.objects.filter(id__in=extra_ids)
            extra_names_prices = [{'name': extra.name, 'price': extra.price} for extra in extra_items]
            item['selected_extra_items'] = extra_names_prices
            
            # Update selected_type_items with names and prices of TypeItems
            type_items = MenuItemTypeItem.objects.filter(id__in=type_ids)
            type_names_prices = [{'name': type_item.name, 'price': type_item.price} for type_item in type_items]
            item['selected_type_items'] = type_names_prices

            # Rename menu_item_id to menu_item_name
            menu_item_id = item.pop('menu_item_id', None)
            if menu_item_id:
                try:
                    menu_item = MenuItem.objects.get(id=menu_item_id)
                    item['menu_item_name'] = menu_item.name
                    # item['menu_item_image'] = menu_item.image.url
                    
                except MenuItem.DoesNotExist:
                    pass
            

        self.items = cart_items
        self.total_price = self.cart.total_price
        self.order_mode = self.cart.order_mode
        self.restaurant = self.cart.restaurant

    def save(self, *args, **kwargs):
        if not self.pk and self.cart:
            self.update_from_cart()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.first_name} {self.customer.last_name}"




class DeliveryDetails(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    post_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    lane = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    house_number = models.CharField(max_length=255, blank=True, null=True)
    floor = models.CharField(max_length=255, blank=True, null=True)
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

