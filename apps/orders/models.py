from django.db import models

from apps.common.models import BaseModel
from apps.orders.choices import FLWRefundStatus, PaymentGateway, PaymentStatus, PaystackRefundStatus, ShippingStatus
from apps.profiles.models import Profile
from apps.shop.models import Product


class Order(BaseModel):
    customer = models.ForeignKey(
        Profile, on_delete=models.PROTECT, related_name="orders"
    )

    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentGateway.choices, default="PAYSTACK"
    )
    shipping_status = models.CharField(
        max_length=20, choices=ShippingStatus.choices, default=ShippingStatus.PENDING
    )
    
    # Refund status
    paystack_refund_status = models.CharField(
        max_length=20, choices=PaystackRefundStatus.choices, blank=True
    )
    flw_refund_status = models.CharField(
        max_length=20, choices=FLWRefundStatus.choices, blank=True
    )
    
    date_delivered = models.DateField(null=True, blank=True)

    # flw
    transaction_id = models.CharField(max_length=50, blank=True)
    reference = models.CharField(max_length=50, unique=True)
    
    # paystack
    payment_ref = models.CharField(max_length=50, unique=True)
    
    tracking_number = models.CharField(max_length=50, blank=True, unique=True)

    # Shipping address details
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    shipping_fee = models.PositiveSmallIntegerField(
        default=0
    )  # if delivery fee changes, amount is preserved
    shipping_time = models.CharField(max_length=50, default="1-3 business days")
    phone_number = models.CharField()
    postal_code = models.CharField(max_length=20)

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
