from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.common.models import BaseModel
from apps.orders.choices import DiscountChoices
from apps.orders.models.order import Order
from apps.profiles.models import Profile
from apps.shop.models import Product


class Discount(BaseModel):
    name = models.CharField(max_length=20)
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountChoices.choices,
        default=DiscountChoices.PERCENTAGE,
    )
    value = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    @property
    def is_active(self):
        return timezone.now() < self.end_date

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date!")

        if self.discount_type == DiscountChoices.TIERED and self.value != 0:
            raise ValidationError(
                "The value must be 0 when the discount type is 'tiers'."
            )

        if self.discount_type == DiscountChoices.PERCENTAGE and self.value > 100:
            raise ValidationError({"value": "Percentage discount cannot exceed 100%"})

    def __str__(self):
        return f"{self.name}"


class ProductDiscount(BaseModel):
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name="discounts"
    )
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="product"
    )

    def clean(self):
        if not self.discount.is_active:
            raise ValidationError(
                {"discount": f"The discount '{self.discount.name}' is expired."}
            )

    def __str__(self):
        return f"{self.product.name} - {self.discount.name}"


class TieredDiscount(BaseModel):
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name="tiers"
    )
    min_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount_percentage = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(99)]
    )
    free_shipping = models.BooleanField(default=False)

    def clean(self):
        if not self.discount.is_active:
            raise ValidationError(f"The discount '{self.discount.name}' is expired.")

        if self.free_shipping and self.discount_percentage:
            raise ValidationError(
                "Tiered discount cannot have both discount percentage and free shipping."
            )

        if not self.free_shipping and not self.discount_percentage:
            raise ValidationError(
                "Tiered discount must have either discount percentage or free shipping."
            )

    def __str__(self):
        if self.free_shipping:
            return f"Spend {self.min_amount}, get Free Shipping"
        else:
            return f"Spend {self.min_amount}, get {self.discount_percentage}% off"


class Coupon(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name="coupons"
    )
    usage_limit = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    used_count = models.PositiveSmallIntegerField(default=0)

    def clean(self):
        if self.discount.discount_type in [
            DiscountChoices.FREE_SHIPPING,
            DiscountChoices.TIERED,
        ]:
            raise ValidationError(
                f"Coupon discount type has to be 'fixed amount' or 'percentage'"
            )

        if not self.discount.is_active:
            raise ValidationError(f"The discount '{self.discount.name}' is expired.")

    @property
    def is_valid(self):
        return self.discount.is_active and (self.used_count < self.usage_limit)

    def __str__(self):
        return self.code


class CouponUsage(BaseModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="coupon_usages"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="coupon_usages"
    )

    class Meta:
        unique_together = ("coupon", "order")

    def __str__(self):
        return f"{self.user} used {self.coupon} on order {self.order.id}"


# Do this in views or serializers so it calls the clean()- test it
# product_discount = ProductDiscount(discount=discount, product=product)
# product_discount.full_clean()  # This will trigger the clean() method
# product_discount.save()
