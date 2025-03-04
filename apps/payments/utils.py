import hashlib, requests, logging
from decouple import config

from apps.orders.choices import (
    FLWRefundStatus,
    PaymentGateway,
    PaymentStatus,
    PaystackRefundStatus,
)
from apps.orders.models import Order
from apps.payments.tasks import refund_failed, refund_pending, refund_processed, refund_success

logger = logging.getLogger(__name__)


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


def issue_refund(payment_method, tx_ref, transaction_id=None):
    if payment_method == PaymentGateway.PAYSTACK:
        return issue_paystack_refund(tx_ref)
    elif payment_method == PaymentGateway.FLUTTERWAVE:
        return issue_flutterwave_refund(transaction_id)
    else:
        raise ValueError("Unsupported payment gateway.")

# PAYSTACK

def issue_paystack_refund(tx_ref):
    url = "https://api.paystack.co/refund"
    headers = {
        "Authorization": f"Bearer {config("PAYSTACK_TEST_SECRET_KEY")}"
    }  # TODO: CHANGE IN PRODUCTION
    data = {"transaction": tx_ref}  # full refund since amount isn't passed
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json().get("data", {})
        refund_status = response_data.get("status")

        if refund_status == "pending":
            return {
                "status": "pending",
                "message": "Refund initiated, waiting for processor",
            }

        else:
            raise ValueError(f"Unexpected refund status: {refund_status}")
    else:
        raise Exception(f"Error issuing refund: {response}")

# FLUTTERWAVE
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
            return {
                "status": "completed",
                "message": "Refund successful",
            }
        elif refund_status == "failed":
            return {
                "status": "failed",
                "message": "Refund failed",
            }
        else:
            raise Exception(f"Unexpected refund status: {refund_status}")

    else:
        raise Exception(f"Error issuing refund: {response.text}")


# @require_POST
# @csrf_exempt
# def flutterwave_refund_callback(request):
#     try:
#         payload = json.loads(request.body)
#     except json.JSONDecodeError:
#         return HttpResponse(status=400)  # Bad Request

#     # Extract relevant data
#     refund_status = payload.get("data", {}).get("status")
#     transaction_id = payload.get("data", {}).get("tx_ref")
#     refund_id = payload.get("data", {}).get("id")

#     try:
#         # Find the associated order
#         order = Order.objects.get(payment_ref=transaction_id)

#         # Update the order's payment status based on the refund status
#         if refund_status == "SUCCESSFUL":
#             order.payment_status = PaymentStatus.REVERSED
#             order.save()
#         elif refund_status == "FAILED":
#             order.payment_status = PaymentStatus.SUCCESSFUL  # Revert to successful
#             order.save()
#         else:
#             logger.warning(f"Unhandled refund status: {refund_status}")

#     except Order.DoesNotExist:
#         logger.error(f"Order not found for transaction ID: {transaction_id}")

#     return HttpResponse(status=200)  # OK


def handle_refund_pending_paystack(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.PENDING
        order.save()
        refund_pending.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")


def handle_refund_processing_paystack(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.PROCESSING
        order.save()
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")


def handle_refund_failed_paystack(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.FAILED
        order.save()
        refund_failed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")


def handle_refund_processed_paystack(data):
    transaction_id = data.get("transaction", {}).get("id")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.paystack_refund_status = PaystackRefundStatus.PROCESSED
        order.payment_status = PaymentStatus.REFUNDED
        order.save()
        refund_processed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")


# FLUTTERWAVE
def handle_refund_success_flw(data):
    transaction_id = data.get("tx_ref")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.payment_status = PaymentStatus.REFUNDED
        order.flw_refund_status = FLWRefundStatus.COMPLETED
        order.save()
        refund_success.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")


def handle_refund_failed_flw(data):
    transaction_id = data.get("tx_ref")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.flw_refund_status = FLWRefundStatus.FAILED
        order.save()
        refund_failed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")
