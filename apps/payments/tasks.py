from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from apps.orders.models import Order


@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    order = Order.objects.get(id=order_id)
    user = order.customer.user
    subject = f"Clothing Store - Invoice no. {order.id}"
    context = {
        "order": order,
    }
    message = render_to_string("orders/emails/order_paid.html", context)

    # Generate PDF
    html = render_to_string(
        "orders/order/pdf.html",
        {
            "order": order,
        },
    )
    out = BytesIO()
    stylesheets = [weasyprint.CSS(finders.find("assets/css/pdf.css"))]
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
