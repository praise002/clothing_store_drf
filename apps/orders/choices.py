from django.db import models


class ShippingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = (
        "processing",
        "Processing",
    )  # once order is confirmed shipping status is set to processing by the admin
    IN_TRANSIT = "in_transit", "In Transit"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = (
        "cancelled",
        "Cancelled",
    )  # when user cancels order after payment we set shipping status to cancelled


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SUCCESSFULL = "successfull", "Successfull"
    CANCELLED = "cancelled", "Cancelled"  # user cancels the payment on the payment page
    FAILED = "failed", "Failed"  # payment failed due to credit card issues, etc
    REFUNDED = "refunded", "Refunded"  # user cancels order and payment is refunded


class PaymentGateway(models.TextChoices):
    PAYSTACK = "paystack", "paystack"
    FLUTTERWAVE = "flutterwave", "flutterwave"


class PaystackRefundStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    FAILED = "failed", "Failed"
    PROCESSED = "processed", "Processed"


class FLWRefundStatus(models.TextChoices):
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
