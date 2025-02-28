from io import BytesIO
from django.shortcuts import get_object_or_404
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from apps.orders.models import Order

from apps.orders.models import Order

from apps.payments.utils import generate_tracking_number


@shared_task
def process_cancelled_failed_payment(payment_status, order):
    """Update the payment status if failed or cancelled"""
    if payment_status.lower() == "failed":
        order.payment_status = "failed"
        order.save()
    elif payment_status.lower() == "cancelled":
        order.payment_status = "cancelled"
        order.save()
    order_pending_cancellation.delay(order.id)


@shared_task
def process_successful_payment(order_id, transaction_id=None):
    """
    Process successful payment asynchronously:
    1. Update order statuses
    2. Generate tracking number
    3. Save order changes
    """
    
    order = get_object_or_404(Order, id=order_id)
    if order.payment_method == "flutterwave":
        order.transaction_id = transaction_id
        
    order.shipping_status = "processing"
    order.payment_status = "successfull"
    tracking_number = generate_tracking_number()
    order.tracking_number = tracking_number
    order.save()


@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    # TODO: USE TRY-EXCEPT
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


@shared_task
def order_pending_cancellation(order_id):
    order = Order.objects.get(id=order_id)
    user = order.customer.user
    subject = f"Order Pending Cancellation - Order #{order.id}"
    context = {
        "order": order,
    }
    message = render_to_string("orders/emails/order_pending_cancellation.html", context)

    # Send email with PDF attachment
    email_message = EmailMessage(subject=subject, body=message, to=[user.email])

    # Set the content type to HTML for the body
    email_message.content_subtype = "html"

    # Send the email
    email_message.send(fail_silently=False)


@shared_task
def refund_pending(order_id):
    pass


@shared_task
def refund_failed(order_id):
    pass


@shared_task
def refund_processed(order_id):
    pass
