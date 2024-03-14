from django.db import models
from customer_app.models import Customer
from restaurant_app.models import Restaurant, MenuItem, Category, RestaurantTable
from cart_app.models import Cart
from payment_app.models import PaymentWay

# from delivery_app.models import DeliveryMan

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    delivery_man = models.ForeignKey('delivery_app.DeliveryMan', on_delete=models.CASCADE)
    payment_way = models.ForeignKey('payment_app.PaymentWay', on_delete=models.CASCADE)
    pick_time = models.DateTimeField(null=True, blank=True)
    coupon_code = models.CharField(max_length=255, blank=True, null=True)
    delivery_address = models.ForeignKey('DeliveryAddress', on_delete=models.CASCADE, related_name='orders')
    
    def __str__(self):
        return f"Order #{self.pk} - {self.customer.first_name} {self.customer.last_name}"




class DeliveryAddress(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    house_number = models.CharField(max_length=255)
    post_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"DeliveryAddress #{self.pk} - Order #{self.order.pk}"

class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant_table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reservation #{self.pk} - {self.customer.first_name} {self.customer.last_name}"



class OrderInvoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2)
    restaurant_vat = models.DecimalField(max_digits=5, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"OrderInvoice #{self.pk} - Order #{self.order.pk}"