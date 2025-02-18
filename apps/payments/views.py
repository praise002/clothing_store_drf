import uuid
from decouple import config
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests

from drf_spectacular.utils import extend_schema

from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from apps.orders.models import Order
from apps.payments.serializers import PaymentInitializeSerializer
from apps.payments.utils import compute_payload_hash
import logging

logger = logging.getLogger(__name__)

tags = ["Payment"]


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
def payment_callback(request):
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
        Order.objects.get(reference=tx_ref)
    except Order.DoesNotExist:
        logger.error(f"Order not found for reference: {tx_ref}.")
        return Response(
            {"status": "error", "message": "Order not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "status": "success",
            "message": "Once we receive your payment from Flutterwave, we will process it and send you a confirmation email.",
        },
        status=status.HTTP_200_OK,
    )


class InitiatePayment(APIView):
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

        # Generate a unique reference for the payment
        reference = str(uuid.uuid4())

        # Flutterwave API details
        flutterwave_url = config("FLW_URL")
        flutterwave_secret_key = config("FLW_SECRET_KEY")
        redirect_url = "https://ba4a-149-88-18-233.ngrok-free.app/api/v1/payment/callback/"  # TODO: change later

        # Prepare the payload for Flutterwave
        payload = {
            "tx_ref": reference,
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
        order.reference = reference
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
