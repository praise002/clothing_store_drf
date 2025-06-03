import logging
from decimal import Decimal

from django.db import transaction

from apps.discount.models import CouponUsage, ProductDiscount, TieredDiscount
from apps.orders.choices import DiscountChoices
from apps.payments.tasks import payment_successful, process_successful_payment

logger = logging.getLogger(__name__)


def calculate_order_discount(
    subtotal: Decimal, discount_type: str, discount_value: int
) -> Decimal:
    discount_amount = Decimal("0")

    if discount_type == DiscountChoices.PERCENTAGE:
        discount_amount = (discount_value / Decimal("100")) * subtotal

    elif discount_type == DiscountChoices.FIXED_AMOUNT:
        discount_amount = min(discount_value, subtotal)

    return subtotal - discount_amount


def apply_coupon_discount_to_order(coupon, order):
    """
    Applies coupon discount to an order and records the usage.
    """
    with transaction.atomic():
        subtotal = order.calculate_subtotal()
        discount_total = Decimal("0")

        # 1. Calculate discount amount based on type
        discount_type = coupon.discount.discount_type
        discount_value = coupon.discount.value

        discount_total = calculate_order_discount(
            subtotal, discount_type, discount_value
        )

        # 2. Apply the discount
        order.discounted_total = discount_total

        order.save()

        # 3. Record coupon usage
        CouponUsage.objects.create(coupon=coupon, user=order.customer, order=order)

        # 4. Increment usage counter
        coupon.used_count += 1
        coupon.save()

        # Check if the order total is now 0 (100% discount)
        final_total = order.get_total_cost()

        if final_total <= Decimal("0"):
            # If total is 0 or less, automatically mark order as paid
            process_successful_payment.apply_async(
                args=[str(order.id)],
                link=[payment_successful.si(order.id)],
            )
            return

        return


def calculate_product_discount(
    product_price: Decimal, discount_type: str, discount_value: int
) -> Decimal:
    """Calculate the discounted price based on discount type."""
    if discount_type == DiscountChoices.PERCENTAGE:
        discount_amount = (discount_value / Decimal("100")) * product_price

    elif discount_type == DiscountChoices.FIXED_AMOUNT:
        discount_amount = min(discount_value, product_price)

    return product_price - discount_amount


def apply_discount_to_product(product, discount):
    """Apply discount to product if valid product discount exists and is active."""
    product_discount = ProductDiscount.objects.filter(
        product=product, discount=discount
    ).exists()

    if not product_discount or not discount.is_active:
        product.discounted_price = None
        product.save()
        return

    if product_discount:
        # 1. Calculate discount amount based on type
        discount_type = discount.discount_type
        discount_value = discount.value
        product_price = product.price

        discount_total = calculate_product_discount(
            product_price, discount_type, discount_value
        )

        # 2. Apply the discount
        product.discounted_price = discount_total
        product.save()


def apply_discount_to_order(order, discount):
    """
    Applies coupon discount to an order and records the usage.
    """
    with transaction.atomic():
        subtotal = order.calculate_subtotal()
        logger.info(
            f"Checking tiered discounts for order {order.id} with subtotal {subtotal}"
        )
        tiered_discount = (
            TieredDiscount.objects.filter(discount=discount, min_amount__lte=subtotal)
            .order_by("-min_amount")
            .first()
        )

        if tiered_discount and tiered_discount.discount.is_active:
            logger.info(f"Found tiered discount: {tiered_discount}")
            if tiered_discount.free_shipping:
                original_shipping = order.shipping_fee
                order.shipping_fee = 0
                order.save()
                logger.info(
                    f"Applied free shipping to order {order.id}. Original shipping: {original_shipping}"
                )
                return {
                    "discount_type": "free_shipping",
                    "message": f"Free shipping applied! Spend at least {tiered_discount.min_amount} to get free shipping.",
                }
            else:
                discount_amount = (
                    tiered_discount.discount_percentage / Decimal("100")
                ) * subtotal
                order.discounted_total = subtotal - discount_amount
                order.save()
                logger.info(
                    f"Applied {tiered_discount.discount_percentage}% discount to order {order.id}. Saved: {discount_amount}"
                )
                return {
                    "discount_type": "percentage",
                    "message": f"Discount of {tiered_discount.discount_percentage}% applied!",
                }
