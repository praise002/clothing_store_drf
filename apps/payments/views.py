from django.urls import reverse
import uuid, json, requests
from decimal import Decimal
from decouple import config
from django.shortcuts import get_object_or_404
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
from apps.orders.choices import PaymentGateway
from apps.orders.models import Order
from apps.payments.serializers import PaymentInitializeSerializer
from apps.payments.utils import compute_payload_hash

import logging

logger = logging.getLogger(__name__)

tags = ["Payment"]

# FLUTTERWAVE
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
        Order.objects.get(tx_ref=tx_ref)
    except Order.DoesNotExist:
        logger.error(f"Order not found for tx_ref: {tx_ref}.")
        return Response(
            {"status": "error", "message": "Order not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Provide feedback based on the payment status
    if payment_status.lower() == "successful":
        return Response(
            {
                "status": "success",
                "message": "Thank you for your payment. We will confirm it shortly.",
            },
            status=status.HTTP_200_OK,
        )
    elif payment_status.lower() in ["cancelled", "failed"]:
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
        if payment_method.lower() != PaymentGateway.FLUTTERWAVE:
            return Response(
                {
                    "error": f"Invalid payment method. Expected {PaymentGateway.FLUTTERWAVE}",
                    "available_methods": dict(PaymentGateway.choices),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.payment_method = payment_method
        order.save()

        # Generate a unique reference for the payment
        tx_ref = str(uuid.uuid4())

        # Flutterwave API details
        flutterwave_url = config("FLW_URL")
        flutterwave_secret_key = config("FLW_SECRET_KEY")
        
        redirect_url = "https://88de-169-150-218-73.ngrok-free.app/api/v1/payments/flw/payment-callback/"  
        print(request.build_absolute_uri(reverse("payment_callback")))
        # Prepare the payload for Flutterwave
        payload = {
            "tx_ref": tx_ref,
            "amount": str(order.get_total_cost()),
            "currency": "NGN",
            "redirect_url": redirect_url,
            "customer": {
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}",
                "phonenumber": order.phone_number,
            },
            "customizations": {
                "title": "Clothing Store",
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
            logger.info(f"Sending payload to Flutterwave: {payload}")
            response = requests.post(flutterwave_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()
            logger.info(f"Flutterwave response: {response_data}")
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
        if payment_method.lower() != PaymentGateway.PAYSTACK:
            return Response(
                {
                    "error": f"Invalid payment method. Expected {PaymentGateway.PAYSTACK}",
                    "available_methods": dict(PaymentGateway.choices),
                },
                status=status.HTTP_400_BAD_REQUEST,
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
        tx_ref = str(
            uuid.uuid4()
        )  # TODO: VERY UNLIKELY FOR COLLISION BUT TEST FOR COLLISION

        # Associate the reference to the Order record
        order.tx_ref = tx_ref
        order.save()

        metadata = json.dumps(
            {
                "order_id": str(order.id),
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