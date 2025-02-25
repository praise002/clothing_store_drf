from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone
from .models import Order

import logging

logger = logging.getLogger(__name__)


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
    """
    Restore stock, and send emails to customers for orders that are
    shipping status has been pending for 24 hours.
    This includes payment status of failed and cancelled.
    """
    # Define the expiration window (24 hours)
    expiration_window = timedelta(hours=24)

    # Calculate the expiration threshold: 24 hours ago from now
    expiration_threshold = timezone.now() - expiration_window

    # Query for orders that are in "pending", "cancelled", or "failed" status
    # AND were created more than 24 hours ago
    expired_orders = Order.objects.filter(
        shipping_status="pending",
        created__lte=expiration_threshold,
    )

    for order in expired_orders:
        # Restore stock for each order item
        for item in order.items.all():
            product = item.product
            product.in_stock += item.quantity
            product.save()

        # Send cancellation email
        logger.info(f"Restocking expired order {order.id}")
        order_canceled(order.id)


@shared_task
def delete_expired_orders():
    # Define the expiration window (24 hours)
    expiration_window = timedelta(hours=24)

    # Calculate the expiration threshold: 24 hours ago from now
    expiration_threshold = timezone.now() - expiration_window

    # Query for orders that are in "pending", "cancelled", or "failed" status
    # AND were created more than 24 hours ago
    expired_orders = Order.objects.filter(
        shipping_status="pending",
        created__lte=expiration_threshold,
    )

    for order in expired_orders:
        logger.info(f"Deleting expired order {order.id}")
        order.delete()
