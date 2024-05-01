from django.utils import timezone
from django.db import models
from customer_app.models import Customer
from order_app.models import Order
from restaurant_app.models import Restaurant
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class QualityRating(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)

class DeliveryRating(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

class TotalRating(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)
    quality_rating = models.FloatField(default=0)
    delivery_rating = models.FloatField(default=0)
    total_rating = models.FloatField(default=0)

    def calculate_total_rating(self):
        quality_avg = QualityRating.objects.filter(order__restaurant=self.restaurant).aggregate(Avg('rating'))['rating__avg'] or 0
        delivery_avg = DeliveryRating.objects.filter(order__restaurant=self.restaurant).aggregate(Avg('rating'))['rating__avg'] or 0
        
        self.quality_rating = quality_avg
        self.delivery_rating = delivery_avg
        self.total_rating = (quality_avg + delivery_avg) / 2
        self.save()

    def __str__(self):
        return f"{self.restaurant.name} - {self.total_rating}"