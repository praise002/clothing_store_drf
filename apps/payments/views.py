import uuid
import json
import requests
from decimal import Decimal
from decouple import config
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from apps.orders.choices import PaymentGateway, PaymentStatus, ShippingStatus
from apps.orders.models import Order
from apps.payments.serializers import PaymentInitializeSerializer
from apps.payments.tasks import (
    payment_completed,
    process_cancelled_failed_payment,
    process_successful_payment,
)
from apps.payments.utils import compute_payload_hash
from apps.payments.utils import issue_refund
import logging

logger = logging.getLogger(__name__)

tags = ["Payment"]


# FLUTTERWAVE
@extend_schema(
    summary="Payment Callback",
    description="Handles the payment callback from the payment gateway and updates the donation status.",
    responses={
        200: SuccessResponseSerializer,
        400: ErrorDataResponseSerializer,
        404: ErrorResponseSerializer,
    },
    tags=tags,
    auth=[],
)
@api_view(["GET"])
def payment_callback_flw(request):
    payment_status = request.GET.get("status")
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")

    if not all([payment_status, tx_ref, transaction_id]):
        logger.warning("Missing required query parameters in payment_callback.")
        return Response(
            {"status": "error", "message": "Missing required query parameters"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        order = Order.objects.get(tx_ref=tx_ref)
    except Order.DoesNotExist:
        logger.error(f"Order not found for tx_ref: {tx_ref}.")
        return Response(
            {"status": "error", "message": "Order not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Provide feedback based on the payment status
    if payment_status.lower() == "successful":
        order.payment_status = "processing"
        return Response(
            {
                "status": "success",
                "message": "Thank you for your payment. We will confirm it shortly.",
            },
            status=status.HTTP_200_OK,
        )
    elif payment_status.lower() in ["cancelled", "failed"]:
        process_cancelled_failed_payment.delay(payment_status, order)
        return Response(
            {
                "status": "info",
                "message": "Your payment was not completed. Please try again or contact support if needed.",
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "status": "info",
                "message": "We are processing your payment. You will receive a confirmation shortly.",
            },
            status=status.HTTP_200_OK,
        )


class InitiatePaymentFLW(APIView):
    serializer_class = PaymentInitializeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Initiate a payment in flutterwave",
        description="This endpoint allows users to initiate a payment in flutterwave.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=serializer.validated_data["order_id"])
        user = request.user
        payment_method = request.data.get("payment_method")
        if payment_method != PaymentGateway.FLUTTERWAVE:
            return Response(
                {"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST
            )

        order.payment_method = payment_method
        order.save()

        # Generate a unique reference for the payment
        tx_ref = str(uuid.uuid4())

        # Flutterwave API details
        flutterwave_url = config("FLW_URL")
        flutterwave_secret_key = config("FLW_SECRET_KEY")
        redirect_url = "https://ba4a-149-88-18-233.ngrok-free.app/api/v1/payment/callback/"  # TODO: change later

        # Prepare the payload for Flutterwave
        payload = {
            "tx_ref": tx_ref,
            "amount": str(order.get_total_cost()),
            "currency": "NGN",
            "redirect_url": redirect_url,
            "customer": {
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}",
                "phonenumber": user.phone_number,
            },
        }

        # Compute the payload hash
        payload_hash = compute_payload_hash(payload, flutterwave_secret_key)

        # Add the payload hash to the request
        payload["payload_hash"] = payload_hash

        headers = {
            "Authorization": f"Bearer {flutterwave_secret_key}",
            "Content-Type": "application/json",
        }

        # Associate the reference to the Order record
        order.tx_ref = tx_ref
        order.save()

        try:
            # Make a request to Flutterwave
            response = requests.post(flutterwave_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()
            return Response(response_data, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as err:
            logger.error(f"Flutterwave API request failed: {err}", exc_info=True)
            # Handle request exceptions
            return Response(
                {
                    "status": "error",
                    "message": "Payment initiation failed",
                    "details": str(err),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ValueError as err:
            logger.error(
                f"JSON decoding error in Flutterwave API response: {err}", exc_info=True
            )
            # Handle JSON decoding error
            return Response(
                {
                    "status": "error",
                    "message": "Payment initiation failed",
                    "details": str(err),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# PAYSTACK
class InitiatePaymentPaystack(APIView):
    serializer_class = PaymentInitializeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Initiate a payment in paystack",
        description="This endpoint allows users to initiate a payment in paystack.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=serializer.validated_data["order_id"])
        user = request.user
        amount = order.get_total_cost() * Decimal("100")
        payment_method = request.data.get("payment_method")
        if payment_method != PaymentGateway.PAYSTACK:
            return Response(
                {"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST
            )

        order.payment_method = payment_method
        order.save()

        # Paystack API URL
        url = "https://api.paystack.co/transaction/initialize"

        # Paystack secret key from settings
        secret_key = config("PAYSTACK_TEST_SECRET_KEY")

        # Headers for the request
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

        # Generate a unique reference for the payment
        tx_ref = str(uuid.uuid4())

        # Associate the reference to the Order record
        order.tx_ref = tx_ref
        order.save()

        metadata = json.dumps(
            {
                "order_id": order.id,
            }
        )

        # Data to send to Paystack
        data = {
            "email": user.email,
            "amount": int(amount),  # amount in cents
            "reference": tx_ref,
            "metadata": metadata,
        }

        # Make the POST request to Paystack
        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        try:
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()
            return Response(response_data, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as err:
            logger.error(f"Paystack API request failed: {err}", exc_info=True)
            # Handle request exceptions
            return Response(
                {
                    "status": "error",
                    "message": "Payment initiation failed",
                    "details": str(err),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ValueError as err:
            logger.error(
                f"JSON decoding error in Paystack API response: {err}", exc_info=True
            )
            # Handle JSON decoding error
            return Response(
                {
                    "status": "error",
                    "message": "Payment initiation failed",
                    "details": str(err),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# Use webhook instead
class VerifyTransactionView(APIView):
    serializer_class = None

    @extend_schema(
        summary="Verify a payment in paystack",
        description="This endpoint verifies a payment in paystack.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, reference, *args, **kwargs):
        try:
            order = Order.objects.get(tx_ref=reference)
        except Order.DoesNotExist:
            logger.error(f"Order not found for tx_ref: {reference}.")
            return Response(
                {"status": "error", "message": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        url = f"https://api.paystack.co/transaction/verify/{reference}"
        secret_key = config("PAYSTACK_TEST_SECRET_KEY")
        headers = {
            "Authorization": f"Bearer {secret_key}",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["status"] and data["status"] == "success":
                process_successful_payment.delay(order)
                payment_completed.delay(order.id)
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to verify transaction", "details": response.json()},
                status=response.status_code,
            )


# class CancelOrderAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Retrieve the order_id from the request data
#         order_id = request.data.get("order_id", None)
#         if not order_id:
#             return Response(
#                 {"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         # Fetch the order
#         order = get_object_or_404(Order, id=order_id)

#         # Check if the order can be canceled
#         if order.shipping_status in [
#             ShippingStatus.IN_TRANSIT,
#             ShippingStatus.DELIVERED,
#         ]:
#             return Response(
#                 {
#                     "error": "This order cannot be canceled as it is already in transit or delivered."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Issue a refund if the payment was successful
#         if order.payment_status == PaymentStatus.SUCCESSFULL:
#             try:
#                 refund_result = issue_refund(
#                     order.payment_method, order.payment_ref, order.transaction_id
#                 )
#                 order.paystack_refund_status = refund_result
#                 order.flw_refund_status = refund_result  # TODO: MIGHT NEED FIXING
#             except Exception as e:
#                 return Response(
#                     {
#                         "error": f"Failed to issue a refund: {str(e)}. Please contact support."
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         order.shipping_status = ShippingStatus.CANCELLED
#         order.save()

#         # Restore stock for each order item
#         for item in order.items.all():
#             product = item.product
#             product.in_stock += item.quantity
#             product.save()

#         return Response(
#             {"message": f"Order {order_id} has been successfully canceled."},
#             status=status.HTTP_200_OK,
#         )
