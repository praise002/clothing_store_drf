import hashlib
import random
import string
from django.utils.timezone import now

from apps.orders.models import Order

def generate_tracking_number():
    """
    Generate a unique tracking number in the format: NGYYYYMMDDXXXXXX e.g NG20250218167855
    """
    timestamp = now().strftime("%Y%m%d")  # Current date in YYYYMMDD format
    random_string = "".join(random.choices(string.digits, k=6))  # 6 random alphanumeric characters
    tracking_number = f"NG{timestamp}{random_string}"

    # Ensure uniqueness by checking the database
    while Order.objects.filter(tracking_number=tracking_number).exists():
        random_string = "".join(random.choices(string.digits, k=6))
        tracking_number = f"NG{timestamp}{random_string}"

    return tracking_number


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