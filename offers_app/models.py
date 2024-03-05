from django.db import models
# from restaurant_app.models import Restaurant, MenuItem, Category

class Offer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    active_in = models.DateTimeField()
    expire_in = models.DateTimeField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    restaurant = models.ForeignKey('restaurant_app.Restaurant', on_delete=models.CASCADE)

    def __str__(self):
        
        return f"Offer #{self.pk} - {self.title} - Restaurant : {self.restaurant.name}"


# class OfferMenuItem(models.Model):
#     offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
#     menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

# class OfferCategory(models.Model):
#     offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)