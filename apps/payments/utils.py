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


def issue_refund(payment_method, tx_ref, transaction_id=None, amount=None):
    if payment_method == PaymentGateway.PAYSTACK:
        return issue_paystack_refund(tx_ref, amount)
    elif payment_method == PaymentGateway.FLUTTERWAVE:
        return issue_flutterwave_refund(transaction_id)
    else:
        raise ValueError("Unsupported payment gateway.")


# PAYSTACK
def issue_paystack_refund(tx_ref, amount=None):
    url = "https://api.paystack.co/refund"
    headers = {
        "Authorization": f"Bearer {config("PAYSTACK_TEST_SECRET_KEY")}"
    }  # TODO: CHANGE IN PRODUCTION
    data = {"transaction": tx_ref}  # full refund since amount isn't passed

    if amount is not None:
        data["amount"] = int(amount * Decimal("100"))  # partial refund

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json().get("data", {})
        refund_status = response_data.get("status")

        if refund_status == "pending":
            return {
                "status": "pending",
                "message": "Refund initiated, waiting for processor",
            }
        elif refund_status == "processing":
            return {
                "status": "processing",
                "message": "Refund request has been received and is awaiting processing",
            }
        elif refund_status == "failed":
            return {
                "status": "failed",
                "message": "Refund could not be processed. Please contact support",
            }
        elif refund_status == "processed":
            return {
                "status": "processed",
                "message": "Refund has been successfully processed",
            }

        else:
            raise ValueError(f"Unexpected refund status: {refund_status}")
    else:
        raise Exception(f"Error issuing refund: {response}")


# FLUTTERWAVE
def issue_flutterwave_refund(
    transaction_id, amount=None, comments="Order cancellation"
):
    """
    Initiate a refund via Flutterwave.
    Supports both partial and full refunds.
    """
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/refund"
    headers = {
        "Authorization": f"Bearer {config('FLW_SECRET_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "comments": comments,
        "callbackurl": "https://e73a-190-2-141-97.ngrok-free.app/api/v1/payments/flw/refund-callback/",
    }

    # Add the amount field only if it is provided (for partial refunds)
    if amount is not None:
        payload["amount"] = str(int(amount))

    try:
        logger.info(f"Initiating refund for transaction ID: {transaction_id}")
        logger.info(f"Payload: {payload}")
        logger.info(f"Headers: {headers}")
        response = requests.post(url, json=payload, headers=headers)
        print(response)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to initiate Flutterwave refund: {str(e)}")


def handle_refund_pending_paystack(data):
    tx_ref = data.get("transaction_reference")
    try:
        order = Order.objects.get(tx_ref=tx_ref)
        order.refund.paystack_refund_status = PaystackRefundStatus.PENDING
        order.save()
        refund_pending.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {tx_ref}")


def handle_refund_processing_paystack(data):
    tx_ref = data.get("transaction_reference")
    try:
        order = Order.objects.get(tx_ref=tx_ref)
        order.refund.paystack_refund_status = PaystackRefundStatus.PROCESSING
        order.save()
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {tx_ref}")


def handle_refund_failed_paystack(data):
    tx_ref = data.get("transaction_reference")
    try:
        order = Order.objects.get(tx_ref=tx_ref)
        order.refund.paystack_refund_status = PaystackRefundStatus.FAILED
        order.save()
        refund_failed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {tx_ref}")


def handle_refund_processed_paystack(data):
    tx_ref = data.get("transaction_reference")
    try:
        order = Order.objects.get(tx_ref=tx_ref)
        # Restore stock for each order item
        for item in order.items.all():
            product = item.product
            product.in_stock += item.quantity
            product.save()
            
        with transaction.atomic():
            order.refund.paystack_refund_status = PaystackRefundStatus.PROCESSED
            order.payment_status = PaymentStatus.REFUNDED
            order.update_shipping_status(ShippingStatus.CANCELLED)
            order.refund.refund_amount = order.get_total_cost() * (
                order.refund.partial_refund_percentage / 100
                if order.refund.partial_refund_percentage
                else 1
            ) # FIXME: BASED ON REFUND ITEMS
            order.save()
        
        # Trigger the Celery task after the transaction is committed
        transaction.on_commit(lambda: refund_processed.delay(order_id=order.id))
        
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {tx_ref}")


# FLUTTERWAVE
def handle_refund_success_flw(data):
    transaction_id = data.get("tx_ref")
    try:
        order = Order.objects.get(transaction_id=transaction_id)
        order.payment_status = PaymentStatus.REFUNDED
        order.refund.flw_refund_status = FLWRefundStatus.COMPLETED
        order.save()
        refund_success.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")


def handle_refund_failed_flw(data):
    transaction_id = data.get("tx_ref")
    try:
        order = Order.objects.get(transaction_id=transaction_id)
        order.refund.flw_refund_status = FLWRefundStatus.FAILED
        order.save()
        refund_failed.delay(order_id=order.id)
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")
