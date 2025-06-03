from io import BytesIO
from django.db import transaction
import weasyprint, logging
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from apps.orders.choices import PaymentStatus, ShippingStatus
from apps.orders.models import Order

from apps.orders.models import Order

logger = logging.getLogger(__name__)


@shared_task
def process_successful_payment(order_id, transaction_id=None):
    """
    Process successful payment asynchronously:
    1. Update order statuses
    2. Generate tracking number
    3. Save order changes
    """
    try:
        order = Order.objects.get(id=order_id)

        with transaction.atomic():
            if order.payment_method == "flutterwave":
                order.transaction_id = transaction_id

            order.update_shipping_status(ShippingStatus.PROCESSING)
            order.payment_status = PaymentStatus.SUCCESSFUL
            order.save()  # This triggers the trackingnumber signal
            logger.info(
                f"Order {order.id} {order.shipping_status} {order.payment_status} processed successfully. Tracking number: {order.tracking_number}"
            )
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return f"Error: Order {order_id} not found"
    except Exception as e:
        logger.error(f"Error processing payment for order {order_id}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def payment_successful(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    try:
        order = Order.objects.get(id=order_id)
        user = order.customer.user
        subject = f"Payment Confirmed - Order #{order.id}"
        context = {
            "order": order,
        }
        message = render_to_string("orders/emails/payment_successful.html", context)

        # Generate PDF
        html = render_to_string(
            "orders/order/pdf.html",
            {
                "order": order,
            },
        )
        out = BytesIO()
        stylesheets = [weasyprint.CSS(finders.find("pdf.css"))]
        weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

        # Prepare the PDF for attachment
        pdf_attachment = out.getvalue()  # Get PDF content
        pdf_filename = f"invoice_{order.id}.pdf"  # Set the file name for the attachment

        # Send email with PDF attachment
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])

        # Attach PDF to the email
        email_message.attach(pdf_filename, pdf_attachment, "application/pdf")

        # Set the content type to HTML for the body
        email_message.content_subtype = "html"

        # Send the email
        email_message.send(fail_silently=False)

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return f"Error: Order {order_id} not found"

    except Exception as e:
        logger.error(f"Failed to send payment successful: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def order_pending_cancellation(order_id):
    try:
        order = Order.objects.get(id=order_id)
        user = order.customer.user
        subject = f"Order Pending Cancellation - Order #{order.id}"
        context = {
            "order": order,
        }
        message = render_to_string(
            "orders/emails/order_pending_cancellation.html", context
        )

        # Send email with PDF attachment
        email_message = EmailMessage(subject=subject, body=message, to=[user.email])

        # Set the content type to HTML for the body
        email_message.content_subtype = "html"

        # Send the email
        email_message.send(fail_silently=False)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return f"Error: Order {order_id} not found"
    except Exception as e:
        logger.error(f"Failed to send payment pending cancellation: {str(e)}")
        return f"Error: {str(e)}"
