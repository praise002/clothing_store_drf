from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


from apps.shop.models import Category, Product

User = get_user_model()


# Enum for discount_type
class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED_AMOUNT = "fixed_amount", "Fixed Amount"
    TIERED_DISCOUNT = "tiered_discount", "Tiered Discount"
    FIRST_TIME_PURCHASE = "first_time_purchase", "First Time Purchase"
    FREE_SHIPPING = "free_shipping", "Free Shipping"


class Discount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE
    )
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # 0-100 for percentage, fixed amount, etc.
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveSmallIntegerField()
    used_count = models.PositiveSmallIntegerField(default=0)

    def is_active(self):
        now = timezone.now()
        return (
            self.start_date <= now <= self.end_date
            and self.used_count <= self.usage_limit
        )

    def __str__(self):
        return self.name


class DiscountAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )  # Ensures one discount per product
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        constraints = [
            # models.UniqueConstraint(
            #     fields=["product"],  # Ensures one discount per product
            #     name="unique_product_discount",
            # ),
            models.UniqueConstraint(
                fields=["category"],  # Ensures one discount per category
                name="unique_category_discount",
                condition=models.Q(
                    product__isnull=True
                ),  # Only enforce if product is null
            ),
        ]

    def clean(self):
        # Custom validation to ensure either product or category is set, but not both
        if self.product and self.category:
            raise ValidationError(
                "A discount cannot be applied to both a product and a category."
            )
        if not self.product and not self.category:
            raise ValidationError(
                "A discount must be applied to either a product or a category."
            )

    def save(self, *args, **kwargs):
        self.clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.discount.name} - {self.product or self.category}"

class OrderDiscount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    order_id = models.UUIDField(unique=True)
    
class TieredDiscount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    min_amount = models.PositiveIntegerField()


class FirstPurchaseDiscount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)


class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    usage_limit = models.PositiveIntegerField()
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        now = timezone.now()
        return now <= self.expires_at and self.usage_count <= self.usage_limit

    def __str__(self):
        return self.code


class UserCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user", "coupon"),)
