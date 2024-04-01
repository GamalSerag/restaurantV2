from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart, Order

@receiver(post_save, sender=Cart)
def update_order_from_cart(sender, instance, created, **kwargs):
    if not created:
        order = Order.objects.filter(cart=instance).first()
        if order:
            order.update_from_cart()
            order.save()