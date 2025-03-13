from django.db import models
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from apps.common.models import BaseModel
from apps.orders.choices import FLWRefundStatus, PaystackRefundStatus, ReturnMethod


class Return(BaseModel):
    reason = models.TextField()
    image = CloudinaryField(
        "return_image",
        folder="returns/",
        # validators=[validate_file_size],
        null=True,
        blank=True,
    )
    return_method = models.CharField(
        max_length=20,
        choices=ReturnMethod.choices,
        default=ReturnMethod.SEND_BY_YOURSELF,
    )
    tracking_number = models.CharField(max_length=50, blank=True)
    request_time = models.DateTimeField(auto_now_add=True)


class Refund(BaseModel):
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Refund status
    paystack_refund_status = models.CharField(
        max_length=20, choices=PaystackRefundStatus.choices, blank=True
    )
    flw_refund_status = models.CharField(
        max_length=20, choices=FLWRefundStatus.choices, blank=True
    )
    
    def clean(self):
        if self.paystack_refund_status and self.flw_refund_status:
            raise ValidationError(
                "Refund status cannot be set for both Paystack and Flutterwave."
            )
