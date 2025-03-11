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
    PENDING = "pending", "pending"
    SUCCESSFUL = "successful", "successful"
    CANCELLED = "cancelled", "cancelled"  # payment cancelled due to payment failure or other reasons
    REFUNDED = "refunded", "refunded"  # user cancels order and payment is refunded


class PaymentGateway(models.TextChoices):
    PAYSTACK = "paystack", "paystack"
    FLUTTERWAVE = "flutterwave", "flutterwave"


class PaystackRefundStatus(models.TextChoices):
    PENDING = "pending", "pending"
    PROCESSING = "processing", "processing"
    FAILED = "failed", "failed"
    PROCESSED = "processed", "processed"


class FLWRefundStatus(models.TextChoices):
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"

class ReturnMethod(models.TextChoices):
    SEND_BY_YOURSELF = "send by yourself", "send by yourself"
    # PICKUP_BY_COMPANY = "pickup by company", "pickup by company"