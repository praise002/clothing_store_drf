from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone
from .models import Order


@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)
    user = order.customer.user
    subject = f"Order nr. {order.id}"
    context = {
        "order": order,
    }
    message = render_to_string("orders/emails/order_placed.html", context)
    email_message = EmailMessage(subject=subject, body=message, to=[user.email])
    email_message.content_subtype = "html"
    email_message.send(fail_silently=False)

def order_canceled(order_id): 
    order = Order.objects.get(id=order_id)
    user = order.customer.user
    subject = f"Canceled Order nr. {order.id} - Your order could not be completed"
    context = {
        "order": order,
        "frontend_url": settings.FRONTEND_URL,
    }
    message = render_to_string("orders/emails/order_canceled.html", context)
    email_message = EmailMessage(subject=subject, body=message, to=[user.email])
    email_message.content_subtype = "html"
    email_message.send(fail_silently=False)
    
@shared_task
def cancel_expired_orders():
    expiration = timezone.now() + timedelta(hours=24)
    expired_orders = Order.objects.filter(
        payment_status="pending", # Check if the order is not paid
        created__gt=expiration  # Check expiration
    )

    for order in expired_orders:
        # Restore stock for each order item
        for item in order.items.all():
            product = item.product
            product.in_stock += item.quantity
            product.save()
        
        # Send cancellation email and delete order
        print(f"Cancelling expired order {order.id}") # TODO: REMOVE LATER
        order_canceled(order.id)
        order.delete()