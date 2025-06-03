from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone

from apps.orders.choices import PaymentStatus
from apps.payments.tasks import order_pending_cancellation
from apps.orders.models import Order

import logging

logger = logging.getLogger(__name__)


@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    try:
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
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return f"Error: Order {order_id} not found"
    except Exception as e:
        logger.error(f"Failed to send payment confirmation: {str(e)}")
        return f"Error: {str(e)}"


def order_canceled(order_id):
    try:
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
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return f"Error: Order {order_id} not found"
    except Exception as e:
        logger.error(f"Failed to send cancelation confirmation: {str(e)}")
        return f"Error: {str(e)}"


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

    # Query for orders that are in "pending", status
    # AND were created more than 24 hours ago
    expired_orders = Order.objects.filter(
        payment_status="pending",
        created__lt=expiration_threshold,
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
        order.payment_status = PaymentStatus.CANCELLED
        order.save()


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
        created__lt=expiration_threshold,
    )

    for order in expired_orders:
        logger.info(f"Deleting expired order {order.id}")
        order.delete()


@shared_task
def check_pending_orders():
    """
    Periodically check for pending orders and send an email notification if not already sent.
    """
    try:
        threshold = timezone.now() - timedelta(hours=1)
        pending_orders = Order.objects.filter(
            created__lt=threshold, payment_status="pending", pending_email_sent=False
        )

        order_ids = list(pending_orders.values_list("id", flat=True))
        logger.info(f"Found {len(order_ids)} pending cancellation orders: {order_ids}")

        if order_ids:
            logger.info("Sending pending cancellation emails")

        for order_id in order_ids:
            logger.info(f"Sending pending cancellation email for order {order_id}")
            order_pending_cancellation(order_id)
            Order.objects.filter(id__in=order_ids).update(pending_email_sent=True)

    except Exception as e:
        logger.error(f"Task failed: {e}")
        return f"Error: {str(e)}"
