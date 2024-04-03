from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CartItem

@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_total_price(sender, instance, **kwargs):
    cart = instance.cart
    total_price = cart.calculate_total_price()
    # cart.total_price = total_price
    print(f'FROM SIGNALS total price ={total_price}')
    cart.save()


@receiver(post_save, sender=CartItem)
def update_cartitem_total_price(sender, instance, created, **kwargs):
    print(kwargs)
    if not created and kwargs.get('update_fields') is not None and 'quantity' in kwargs['update_fields']:
        cart = instance.cart
        print(f'FROM SIGNALS  ={cart}')
        print('UPDATE SIGNAL CALLED')
        # Calculate the new total price after discount
        instance.total_price_after_discount = instance.price_after_discount * Decimal(instance.quantity)
        instance.save()