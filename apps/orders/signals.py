import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.orders.choices import PaymentStatus
from apps.orders.models import Order, TrackingNumber
from apps.orders.utils import generate_tracking_number

logger = logging.getLogger(__name__)


# created - just created or existing record that is being updated
# created=True - instance is being saved for the first time
# created=False - the instance already exists in the db
@receiver(post_save, sender=Order)
def assign_tracking_number_on_payment_success(sender, instance, created, **kwargs):
    """
    Generate and assign a tracking number when payment is successful.
    """
    if (
        not created
        and instance.payment_status == PaymentStatus.SUCCESSFUL
        and not instance.tracking_number
    ):
        tracking_number = TrackingNumber.objects.create(
            number=generate_tracking_number()
        )
        instance.tracking_number = tracking_number
        instance.save()
        logger.info(f"Generated tracking number: {tracking_number}")
