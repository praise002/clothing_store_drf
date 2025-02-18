from django.db import models


from apps.common.models import BaseModel

from apps.profiles.models import Profile
from apps.shop.models import Product


class ShippingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = (
        "processing",
        "Processing",
    )  # once order is confirmed shipping status is set to processing by the admin
    IN_TRANSIT = "in_transit", "In Transit"
    DELIVERED = "delivered", "Delivered"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = (
        "confirmed",
        "Confirmed",
    )  # order confirmed after successful payment and stock verification
    CANCELLED = (
        "cancelled",
        "Cancelled",
    )  # order canceled by admin due to low stock or no payment
    FAILED = (
        "failed",
        "Failed",
    )  


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    REFUNDED = "refunded", "Refunded"


class Order(BaseModel):
    customer = models.ForeignKey(
        Profile, on_delete=models.PROTECT, related_name="orders"
    )

    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text="Current status of the order in the fulfillment process",
    )
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    shipping_status = models.CharField(
        max_length=20, choices=ShippingStatus.choices, default=ShippingStatus.PENDING
    )

    transaction_id = models.CharField(max_length=50, blank=True)
    reference = models.CharField(max_length=50, unique=True)
    tracking_number = models.CharField(max_length=50, blank=True, unique=True)

    # Shipping
    state = models.CharField()
    shipping_fee = models.PositiveSmallIntegerField(
        default=0
    )  # if delivery fee changes, amount is preserved
    phone_number = models.CharField()

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.full_name}"

    def get_total_cost(self):
        """Calculate the total cost."""
        return sum(item.get_cost() for item in self.items.all()) + self.shipping_fee


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product} in order {self.order.id}"
