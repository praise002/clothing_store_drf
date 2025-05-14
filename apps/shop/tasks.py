from celery import shared_task

from django.utils import timezone

from apps.discount.models import Discount, ProductDiscount

import logging

logger = logging.getLogger(__name__)


@shared_task
def check_expired_discounts():
    """
    Periodic task to check and update expired discount
    """
    try:
        expired_discounts = Discount.objects.filter(end_date__lt=timezone.now())
        processed_count = 0

        for discount in expired_discounts:
            try:
                product_discount = discount.product
                product = product_discount.product
                product.discounted_price = None
                product.save()
                processed_count += 1
                logger.info(f"Expired discount removed from {product.name}")
            except ProductDiscount.DoesNotExist:
                logger.warning(f"No product discount found for discount {discount.id}")
                continue

        return f"Processed {expired_discounts.count()} expired discounts"
    except Exception as e:
        logger.error(f"Error checking expired discounts: {str(e)}")
        raise
