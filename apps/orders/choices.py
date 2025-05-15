from django.db import models


class DiscountChoices(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED_AMOUNT = "fixed_amount", "Fixed Amount"
    TIERED = "tiered", "Tiered Discount"


class ShippingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = (
        "processing",
        "Processing",
    )  # once order is confirmed shipping status is set to processing by the admin i.e packaging
    SHIPPED = "shipped", "Shipped"  # handed over to a shipping carrier
    IN_TRANSIT = "in_transit", "In Transit"
    OUT_FOR_DELIVERY = (
        "out_for_delivery",
        "Out for delivery",
    )  # with local delivery agent
    DELIVERED = "delivered", "Delivered"

    # CANCELLED = (
    #     "cancelled",
    #     "Cancelled",
    # )  # when user cancels order after payment we set shipping status to cancelled


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "pending"
    SUCCESSFUL = "successful", "successful"
    CANCELLED = (
        "cancelled",
        "cancelled",
    )  # payment cancelled due to payment failure or other reasons
    REFUNDED = "refunded", "refunded"  # user cancels order and payment is refunded


class PaymentGateway(models.TextChoices):
    PAYSTACK = "paystack", "paystack"
    FLUTTERWAVE = "flutterwave", "flutterwave"
