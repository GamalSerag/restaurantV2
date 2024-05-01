from django.core.mail import send_mail
from django.conf import settings
from rest_framework.authentication import TokenAuthentication

def send_order_placed_email(customer_email, order_id):
    subject = 'Order Placed Successfully'
    message = f'Your order with ID {order_id} has been placed successfully.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [customer_email]
    
    send_mail(subject, message, from_email, recipient_list)

def send_order_status_changed_email(customer_email, order_id, new_status):
    subject = 'Order Status Changed'
    message = f'Your order with ID {order_id} has been updated to status: {new_status}.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [customer_email]
    
    send_mail(subject, message, from_email, recipient_list)

