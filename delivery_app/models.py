from django.db import models
from customer_app.models import Customer
# from order_app.models import Order


class DeliveryMan(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    available = models.BooleanField()
    current_location_latitude = models.FloatField(null=True, blank=True)
    current_location_longitude = models.FloatField(null=True, blank=True)


class Delivery(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    delivery_status = models.CharField(max_length=255)
    employee = models.ForeignKey(DeliveryMan, on_delete=models.CASCADE)
    employee_latitude = models.FloatField(null=True, blank=True)
    employee_longitude = models.FloatField(null=True, blank=True)
    order = models.ForeignKey('order_app.Order', on_delete=models.CASCADE)

    def __str__(self):
        return f"Delivery #{self.pk} - Order #{self.order.pk}"

class DeliveryRoute(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2)
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    end_latitude = models.FloatField()
    end_longitude = models.FloatField()
    duration = models.DurationField()

    def __str__(self):
        return f"Delivery Route #{self.pk} - Delivery #{self.delivery.pk}"

