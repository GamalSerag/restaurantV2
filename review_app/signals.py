from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QualityRating, DeliveryRating, TotalRating
from django.db.models import Avg

@receiver(post_save, sender=QualityRating)
def update_total_rating_on_quality_rating(sender, instance, created, **kwargs):
    if created:
        restaurant = instance.restaurant
        total_rating = TotalRating.objects.filter(restaurant=restaurant).first()
        if total_rating:
            total_rating.calculate_total_rating()

@receiver(post_save, sender=DeliveryRating)
def update_total_rating_on_delivery_rating(sender, instance, created, **kwargs):
    if created:
        restaurant = instance.restaurant
        total_rating = TotalRating.objects.filter(restaurant=restaurant).first()
        if total_rating:
            total_rating.calculate_total_rating()