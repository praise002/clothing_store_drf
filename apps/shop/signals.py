import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.discount.models import ProductDiscount
from apps.discount.service import apply_discount_to_product

logger = logging.getLogger(__name__)


# created - just created or existing record that is being updated
# created=True - instance is being saved for the first time
# created=False - the instance already exists in the db
@receiver(post_save, sender=ProductDiscount)
def handle_product_discount_save(sender, instance, created, **kwargs):
    """
    Handle product discount creation and updates.
    """
    apply_discount_to_product(instance.product, instance.discount)
    logger.info(f"Discount applied to: {instance.product.name} {instance.discount}")


@receiver(post_delete, sender=ProductDiscount)
def handle_product_discount_delete(sender, instance, **kwargs):
    """Reset product's discounted price when ProductDiscount is deleted."""
    apply_discount_to_product(instance.product, instance.discount)
    logger.info(f"Discount removed from: {instance.product.name} {instance.discount}")


# @receiver(post_delete, sender=ProductDiscount)
# def handle_product_discount_delete(sender, instance, **kwargs):
#     """Reset product's discounted price when ProductDiscount is deleted."""
#     instance.product.discounted_price = None
#     instance.product.save()
