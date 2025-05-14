from django.db import transaction
from decimal import Decimal
from apps.discount.models import CouponUsage, ProductDiscount
from apps.orders.choices import DiscountChoices


def calculate_order_discount(
    subtotal: Decimal, discount_type: str, discount_value: int
) -> Decimal:
    if discount_type == DiscountChoices.PERCENTAGE:
        discount_amount = (discount_value / Decimal("100")) * subtotal

    elif discount_type == DiscountChoices.FIXED_AMOUNT:
        discount_amount = min(discount_value, subtotal)

    return subtotal - discount_amount


def apply_discount_to_order(coupon, order):
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
