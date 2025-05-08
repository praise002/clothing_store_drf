import hashlib, requests, logging

from django.db import transaction
from decimal import Decimal
from decouple import config
from apps.orders.choices import (
    FLWRefundStatus,
    PaymentGateway,
    PaymentStatus,
    PaystackRefundStatus,
    ShippingStatus,
)
from apps.orders.models import Order
from apps.payments.tasks import (
    refund_failed,
    refund_pending,
    refund_processed,
    refund_success,
)

logger = logging.getLogger(__name__)

REFUND_PERCENTAGE = 50  # 50% refund for partial refunds


def compute_payload_hash(payload, secret_key):
    """
    Compute the payload hash for Flutterwave checksum verification.
    """
    # Concatenate the immutable fields in a specific order
    concatenated_string = (
        f"{payload['amount']}"
        f"{payload['currency']}"
        f"{payload['customer']['email']}"
        f"{payload['tx_ref']}"
    )

    hashed_secret_key = hashlib.sha256(secret_key.encode("utf-8")).hexdigest()

    string_to_be_hashed = concatenated_string + hashed_secret_key
    payload_hash = hashlib.sha256(string_to_be_hashed.encode("utf-8")).hexdigest()

    return payload_hash
