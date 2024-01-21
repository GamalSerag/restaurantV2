from django.db import models
from restaurant_app.models import Restaurant, MenuItem

class Promotion(models.Model):
    timestamps = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    active_in = models.DateTimeField()
    expire_in = models.DateTimeField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Promotion #{self.pk} - {self.title}"

