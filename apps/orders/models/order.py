from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

from apps.common.models import BaseModel
from apps.orders.choices import (
    PaymentGateway,
    PaymentStatus,
    ShippingStatus,
)

from apps.orders.models import TrackingNumber
from apps.profiles.models import Profile
from apps.shop.models import Product
import logging

logger = logging.getLogger(__name__)


class Order(BaseModel):
    customer = models.ForeignKey(
        Profile, on_delete=models.PROTECT, related_name="orders"
    )

    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentGateway.choices,
    )
    shipping_status = models.CharField(
        max_length=20, choices=ShippingStatus.choices, default=ShippingStatus.PENDING
    )

    transaction_id = models.CharField(max_length=50, blank=True)
    tx_ref = models.CharField(max_length=50, blank=True)

    tracking_number = models.OneToOneField(
        TrackingNumber,
        on_delete=models.PROTECT,  # Allow NULL until the tracking number is generated
        null=True,
        blank=True,
        related_name="order",
    )

    discounted_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total cost after applying discounts",
    )

    # Shipping address details
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    shipping_fee = models.PositiveSmallIntegerField(
        default=0
    )  # if delivery fee changes, amount is preserved
    shipping_time = models.CharField(max_length=50, default="1-3 business days")
    phone_number = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20)

    pending_email_sent = models.BooleanField(default=False)

    # Timestamp fields for each payment status
    processing_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    in_transit_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["payment_status", "shipping_status"]),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.full_name}"

    def calculate_subtotal(self) -> Decimal:
        """Calculate the subtotal (sum of all items before discount and shipping)."""
        return sum(item.get_cost() for item in self.items.all())

    def get_total_cost(self) -> Decimal:
        """Calculate the final total including discount (if any) and shipping fee."""
        base_amount = (
            self.discounted_total
            if self.discounted_total
            else self.calculate_subtotal()
        )

        return base_amount + self.shipping_fee

    def update_shipping_status(self, new_status):
        """
        Update the shipping_status and record the timestamp.
        """
        from django.utils.timezone import now

        if new_status == ShippingStatus.PROCESSING:
            self.processing_at = now()
        elif new_status == ShippingStatus.SHIPPED:
            self.shipped_at = now()
        elif new_status == ShippingStatus.IN_TRANSIT:
            self.in_transit_at = now()
        elif new_status == ShippingStatus.OUT_FOR_DELIVERY:
            self.out_for_delivery_at = now()
        elif new_status == ShippingStatus.DELIVERED:
            self.delivered_at = now()
        elif new_status == ShippingStatus.CANCELLED:
            self.cancelled_at = now()

        # Update the payment_status
        self.shipping_status = new_status
        self.save()


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product} in order {self.order.id}"
