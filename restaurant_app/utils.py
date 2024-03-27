from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

def send_category_request_email(admin_email, subject, message):
    # Construct the email content
    email_message = strip_tags(message)  # Remove HTML tags if any

    # Send the email using Django's send_mail function
    send_mail(
        subject,
        email_message,
        settings.EMAIL_HOST_USER, 
        [admin_email], 
        fail_silently=False,
    )

def category_request_email_approval(request, instance, is_approved):
    if is_approved:
        subject = "Category Request Status: Approved"
    else:
        subject = "Category Request Status: Rejected"

    # Get the admin email from the request.user object
    admin_email = instance.requested_by.user.email

    # Construct the message using superadmin_notes from CategoryAdminRequest
    message = f"Category Request Status: {'Approved' if is_approved else 'Rejected'}\n\n"
    message += f"Notes from Superadmin: {instance.superadmin_notes if not is_approved else 'Thank you For your request'}\n"

    # Send the email
    send_category_request_email(admin_email, subject, message)