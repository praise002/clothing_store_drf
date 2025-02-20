from django.db import models


class ShippingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = (
        "processing",
        "Processing",
    )  # once order is confirmed shipping status is set to processing by the admin
    IN_TRANSIT = "in_transit", "In Transit"
    DELIVERED = "delivered", "Delivered"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SUCCESSFULL = "successfull", "Successfull"
    CANCELLED = "cancelled", "Cancelled"  # user cancels the payment on the payment page
    FAILED = "failed", "Failed"  # payment failed due to credit card issues, etc
    REFUNDED = "refunded", "Refunded"


class PaymentGateway(models.TextChoices):
    PAYSTACK = "paystack", "Paystack"
    FLUTTERWAVE = "flutterwave", "Flutterwave"
