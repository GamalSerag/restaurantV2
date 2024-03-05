from django.db import models
from customer_app.models import Customer
from restaurant_app.models import MenuItem, Restaurant

class Review(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    comment = models.TextField()
    rate = models.IntegerField()
    type = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Review #{self.pk} - {self.customer.first_name} {self.restaurant_customer.last_name}"

class DeliveryReview(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey('order_app.Order', on_delete=models.CASCADE)
    comment = models.TextField()
    rate = models.IntegerField()

    def __str__(self):
        return f"Delivery Review #{self.pk} - {self.customer.first_name} {self.customer.last_name}"



