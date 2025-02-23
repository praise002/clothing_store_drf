import hashlib, random, string, requests, logging
from decouple import config
from django.utils.timezone import now

from apps.orders.choices import PaystackRefundStatus
from apps.orders.models import Order
from apps.payments.tasks import refund_failed, refund_pending, refund_processed

logger = logging.getLogger(__name__)

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

def issue_refund(payment_gateway, payment_ref=None, transaction_id=None):
    if payment_gateway == "paystack":
        issue_paystack_refund(payment_ref)
    elif payment_gateway == "flutterwave":
        issue_flutterwave_refund(transaction_id)
    else:
        raise ValueError("Unsupported payment gateway.")

def issue_paystack_refund(payment_ref):
    url = "https://api.paystack.co/refund"
    headers = {"Authorization": f"Bearer {config("PAYSTACK_TEST_SECRET_KEY")}"} # TODO: CHANGE IN PRODUCTION
    data = {"transaction": payment_ref} # full refund since amount isn't passed
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json().get("data", {})
        refund_status = response_data.get("status")
        
        if refund_status == "pending":
            return "pending" # Refund initiated, waiting for processor
        else:
            raise ValueError(f"Unexpected refund status: {refund_status}")
    else:
        raise Exception(f"Error issuing refund: {response}")
# It takes 10 business days to receive their funds when it is marked as processed

def issue_flutterwave_refund(transaction_id, callback_url=None):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/refund"
    headers = {"Authorization": f"Bearer {config('FLUTTERWAVE_SECRET_KEY')}"}
    data = {}
    
    # # Include the callback URL if provided
    if callback_url:
        data["callbackurl"] = callback_url
        
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        refund_status = response_data.get("data", {}).get("status")
        if refund_status == "completed":
            return "completed"
        elif refund_status == "failed":
            return "failed"
        else:
            raise Exception(f"Unexpected refund status: {refund_status}")
        
    else:
        raise Exception(f"Error issuing refund: {response.text}")

@require_POST
@csrf_exempt
def flutterwave_refund_callback(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)  # Bad Request

    # Extract relevant data
    refund_status = payload.get("data", {}).get("status")
    transaction_id = payload.get("data", {}).get("tx_ref")
    refund_id = payload.get("data", {}).get("id")

    try:
        # Find the associated order
        order = Order.objects.get(payment_ref=transaction_id)

        # Update the order's payment status based on the refund status
        if refund_status == "SUCCESSFUL":
            order.payment_status = PaymentStatus.REVERSED
            order.save()
        elif refund_status == "FAILED":
            order.payment_status = PaymentStatus.SUCCESSFUL  # Revert to successful
            order.save()
        else:
            logger.warning(f"Unhandled refund status: {refund_status}")

    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")

    return HttpResponse(status=200)  # OK  

def handle_refund_pending(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.PENDING
        order.save()
        refund_pending.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")

def handle_refund_processing(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.PROCESSING  
        order.save()
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")

def handle_refund_failed(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.FAILED
        order.save()
        refund_failed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")

def handle_refund_processed(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.PROCESSED
        order.save()
        refund_processed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")