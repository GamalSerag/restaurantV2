from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CartItem

@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_total_price(sender, instance, **kwargs):
    cart = instance.cart
    # total_price = cart.calculate_total_price()  # You need to implement this method in your Cart model
    # cart.total_price = total_price
    # print(total_price)
    # cart.save()