import logging, json, requests, hmac, hashlib


from decouple import config
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response

from apps.orders.models import Order
from apps.payments.models import PaymentEvent
from apps.payments.tasks import payment_completed, process_successful_payment
from apps.payments.utils import (
    handle_refund_failed,
    handle_refund_pending,
    handle_refund_processed,
    handle_refund_processing,
)


logger = logging.getLogger(__name__)

# FLUTTERWAVE


@require_POST
@csrf_exempt
def flw_payment_webhook(request):
    logger.info("Webhook request received.")
    # Step 1: Verify the webhook signature
    secret_hash = config("FLW_SECRET_HASH")
    signature = request.headers.get("verifi-hash")

    if not signature or signature != secret_hash:
        # This request isn't from Flutterwave; discard
        return HttpResponse(status=401)

    # Step 2: Parse the payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload in webhook request.")
        return Response(
            {"status": "error", "message": "Invalid JSON payload"}, status=400
        )

    # Step 3: Extract required fields
    data = payload.get("data", {})
    transaction_id = data.get("id")
    tx_ref = data.get("tx_ref")

    if not all([transaction_id, tx_ref]):
        logger.warning("Missing required fields in webhook payload.")
        return Response(
            {"status": "error", "message": "Missing required fields"}, status=400
        )

    verification_url = (
        f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    )
    headers = {
        "Authorization": f"Bearer {config("FLW_SECRET_KEY")}",
        "Content-Type": "application/json",
    }

    # Step 4: Retrieve the Order record
    try:
        order = Order.objects.get(reference=tx_ref)
    except Order.DoesNotExist:
        logger.error(f"Order not found for reference: {tx_ref}.")
        return Response(
            {"status": "error", "message": "Order not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        # Step 5: Verify the transaction with Flutterwave
        response = requests.get(verification_url, headers=headers)
        response.raise_for_status()
        verification_data = response.json()

        # Step 6: Validate the transaction
        if (
            verification_data["data"]["status"] == "successful"
            and verification_data["data"]["amount"] == payload["data"]["amount"]
            and verification_data["data"]["currency"] == payload["data"]["currency"]
        ):
            # Step 7: Handle idempotency (check if the event has already been processed)
            event_id = payload.get("id")
            existing_event = PaymentEvent.objects.filter(event_id=event_id).exists()

            if existing_event and existing_event.status == payload["data"]["status"]:
                # Duplicate event; discard
                return HttpResponse(status=200)

            # Step 8: Save the event and process it
            PaymentEvent.objects.create(
                event_id=event_id,
                status=payload["data"]["status"],
                amount=payload["data"]["amount"],
                currency=payload["data"]["currency"],
                transaction_id=transaction_id,
            )

            # Step 8: Perform additional processing (e.g., update database, send email)
            process_successful_payment.delay(order, transaction_id)
            payment_completed.delay(transaction_id)

            return HttpResponse(status=200)
        else:
            # Transaction verification failed
            logger.warning("Transaction verification failed.")
            return Response(
                {"status": "error", "message": "Transaction verification failed"},
                status=400,
            )

    except requests.exceptions.RequestException as err:
        # Handle API errors
        error_message = str(err)
        if err.response:
            error_message = err.response.json().get(
                "message", "An error occurred while verifying the transaction."
            )
        logger.error(f"Flutterwave API request failed: {error_message}", exc_info=True)
        return Response({"status": "error", "message": error_message}, status=400)


# PAYSTACK
def validate_paystack_webhook(request):
    """
    Validates the authenticity of a Paystack webhook event.
    Returns True if the event is legitimate, False otherwise.
    """
    secret_key = config("PAYSTACK_TEST_SECRET_KEY")

    # Get the signature from the request header
    signature = request.headers.get("x-paystack-signature")
    if not signature:
        return False  # Missing signature

    # Parse the payload
    try:
        payload = request.body.decode("utf-8")
        payload_json = json.loads(payload)
    except json.JSONDecodeError:
        return False  # Invalid JSON payload

    # Compute the expected signature
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).hexdigest()

    # Compare the signatures
    return hmac.compare_digest(signature, expected_signature)


@require_POST
@csrf_exempt
def paystack_refund_webhook(request):
    # Validate the webhook event
    if not validate_paystack_webhook(request):
        return HttpResponse(status=401)

    # Parse the payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # Process the event
    event_type = payload.get("event")
    data = payload.get("data", {})

    if event_type == "refund.pending":
        handle_refund_pending(data)
    elif event_type == "refund.processing":
        handle_refund_processing(data)
    elif event_type == "refund.failed":
        handle_refund_failed(data)
    elif event_type == "refund.processed":
        handle_refund_processed(data)

    return HttpResponse(status=200)

@require_POST
@csrf_exempt
def flutterwave_webhook(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)  # Bad Request

    event_type = payload.get("event")
    data = payload.get("data", {})

    if event_type == "refund.success":
        handle_refund_success(data)
    elif event_type == "refund.failed":
        handle_refund_failed(data)

    return HttpResponse(status=200)  # OK

def handle_refund_success(data):
    transaction_id = data.get("tx_ref")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.payment_status = PaymentStatus.REVERSED
        order.save()
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")

def handle_refund_failed(data):
    transaction_id = data.get("tx_ref")
    try:
        order = Order.objects.get(payment_ref=transaction_id)
        order.payment_status = PaymentStatus.SUCCESSFUL  # Revert to successful
        order.save()
    except Order.DoesNotExist:
        logger.error(f"Order not found for transaction ID: {transaction_id}")