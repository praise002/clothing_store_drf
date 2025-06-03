import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.profiles.models import ShippingAddress, ShippingFee


@receiver(post_save, sender=ShippingFee)
def update_shipping_addresses(sender, instance, created, **kwargs):
    """
    Update all shipping addresses with the new shipping fee when a ShippingFee is updated.
    """
    # Find all shipping addresses for this state and update them
    ShippingAddress.objects.filter(state=instance.state).update(
        shipping_fee=instance.fee
    )
