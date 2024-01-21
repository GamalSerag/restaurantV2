from django.db import models
from restaurant_app.models import Restaurant
from customer_app.models import Customer
# from order_app.models import Order


class PaymentWay(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class PaymentTransaction(models.Model):
    payment_way = models.ForeignKey(PaymentWay, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    timestamps = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('order_app.Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"PaymentTransaction #{self.pk} - Order #{self.order.pk}"


