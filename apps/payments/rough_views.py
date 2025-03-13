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
from apps.orders.choices import PaymentGateway, PaymentStatus, ShippingStatus
from apps.orders.models import Order
from apps.payments.serializers import PaymentInitializeSerializer
from apps.payments.tasks import (
    order_pending_cancellation,
    payment_successful,
    process_cancelled_failed_payment,
    process_successful_payment,
)
from apps.payments.utils import compute_payload_hash, issue_refund

# from apps.payments.utils import issue_refund
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
        order.payment_status = "processing" # NOTE: REMOVED PROCESSING
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


# https://83b7-149-22-84-153.ngrok-free.app/payments/webhook/
# Use webhook instead
class VerifyTransactionPaystack(APIView):
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
    def get(self, request, reference):
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
            response_data = response.json()
            if response_data["status"] and response_data["data"]["status"] == "success":
                process_successful_payment.apply_async(
                    args=[str(order.id)], link=payment_successful.si(order.id)
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                order_pending_cancellation.delay(order.id)
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to verify transaction", "details": response.json()},
                status=response.status_code,
            )

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, PaymentStatus, FLWRefundStatus
from .tasks import refund_success, refund_failed
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def flutterwave_refund_callback(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            data = json.loads(request.body)
            refund_status = data.get('status')
            transaction_id = data.get('tx_ref')

            # Fetch the order
            try:
                order = Order.objects.get(transaction_id=transaction_id)
                if refund_status == 'completed':
                    order.payment_status = PaymentStatus.REFUNDED
                    order.flw_refund_status = FLWRefundStatus.COMPLETED
                    order.save()
                    refund_success.delay(order_id=order.id)
                elif refund_status == 'failed':
                    order.flw_refund_status = FLWRefundStatus.FAILED
                    order.save()
                    refund_failed.delay(order_id=order.id)
                else:
                    logger.warning(f"Unknown refund status: {refund_status} for transaction ID: {transaction_id}")

                return JsonResponse({"status": "success", "message": "Callback processed successfully."})

            except Order.DoesNotExist:
                logger.error(f"Order not found for transaction ID: {transaction_id}")
                return JsonResponse({"status": "error", "message": "Order not found."}, status=404)

        except Exception as e:
            logger.error(f"Error processing refund callback: {str(e)}")
            return JsonResponse({"status": "error", "message": "An error occurred."}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

class UpdateTrackingNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = ["tracking_number"]
        
class UpdateTrackingNumberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update tracking number for a return request",
        description="Allows a user to add or update the tracking number for their return request.",
        tags=tags,
        responses={
            200: OpenApiResponse(description="Tracking number updated successfully."),
            400: OpenApiResponse(description="Invalid data provided."),
            403: OpenApiResponse(description="Not authorized to update this return request."),
            404: OpenApiResponse(description="Return request not found."),
        },
    )
    def patch(self, request, return_id):
        try:
            return_obj = Return.objects.get(id=return_id)
        except Return.DoesNotExist:
            return Response(
                {"error": "Return request not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Check ownership
        order = return_obj.order_set.first()  # Assuming a reverse relation exists
        if order.customer.user != request.user:
            return Response(
                {"error": "Not authorized to update this return request."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate and update the tracking number
        serializer = UpdateTrackingNumberSerializer(
            return_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Tracking number updated successfully."},
            status=status.HTTP_200_OK,
        )
        
def process_refund_after_tracking_confirmation(return_obj):
    """
    Process the refund after confirming the tracking number.
    """
    if not return_obj.tracking_number:
        raise ValueError("Tracking number is required to process the refund.")

    # Validate tracking number (e.g., via a shipping API)
    is_valid_tracking = validate_tracking_number(return_obj.tracking_number)
    if not is_valid_tracking:
        raise ValueError("Invalid or unconfirmed tracking number.")

    # Get the associated order
    order = return_obj.order_set.first()
    if not order:
        raise ValueError("No order associated with this return request.")

    # Process the refund
    refund_result = issue_refund(
        order.payment_method,
        order.tx_ref,
        order.transaction_id,
        amount=order.get_total_cost(),
    )
    return refund_result

class OrderValidator:
    @staticmethod
    def validate_order(order, user):
        if order.customer.user != user:
            return Response(
                {"error": "Not authorized to cancel this order"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if the order is already canceled
        if order.shipping_status == ShippingStatus.CANCELLED:
            return Response(
                {"error": "This order has already been canceled."},
                status=status.HTTP_409_CONFLICT,
            )

        # Check if the order can be canceled
        if order.shipping_status == ShippingStatus.IN_TRANSIT:
            return Response(
                {
                    "error": "This order cannot be canceled as it is already in transit. Please request a return/refund after receiving the package."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.shipping_status == ShippingStatus.DELIVERED:
            return Response(
                {"message": "Request a return/refund."},
                status=status.HTTP_200_OK,
            )

        return None


class RefundProcessor:
    @staticmethod
    def process_refund(order):
        if order.payment_status == PaymentStatus.SUCCESSFUL:
            try:
                if order.refund.refund_amount:
                    refund_result = issue_refund(
                        order.payment_method,
                        order.tx_ref,
                        order.transaction_id,
                        order.refund.refund_amount,
                    )
                else:
                    refund_result = issue_refund(
                        order.payment_method, order.tx_ref, order.transaction_id
                    )
                return refund_result

            except Exception as e:
                raise Exception(f"Failed to issue a refund: {str(e)}")

        return None


class OrderCancellationService:
    @staticmethod
    def cancel_order(order):
        order.shipping_status = ShippingStatus.CANCELLED
        order.save()

        # Restore stock for each order item
        for item in order.items.all():
            product = item.product
            product.in_stock += item.quantity
            product.save()


class CancelOrderAPIView(APIView):
    serializer_class = None
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cancel an order",
        description="Allows a user to cancel their order. If payment was made, initiates refund.",
        tags=tags,
        responses={
            200: OpenApiResponse(
                description="Order cancelled successfully",
                response=None,
            ),
            400: OpenApiResponse(
                description="Order cannot be cancelled",
                response=None,
            ),
            404: OpenApiResponse(
                description="Order not found",
                response=None,
            ),
            403: OpenApiResponse(
                description="Not authorized to cancel this order",
                response=None,
            ),
        },
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Validate the order
        validation_response = OrderValidator.validate_order(order, request.user)
        if validation_response:
            return validation_response

        # Process refund if payment was successful
        try:
            refund_result = RefundProcessor.process_refund(order)
            if refund_result:
                if order.payment_method == PaymentGateway.PAYSTACK:
                    return Response(
                        {
                            "status": refund_result.get("status"),
                            "message": refund_result.get("message"),
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(refund_result)

        except Exception as e:
            return Response(
                {
                    "error": f"Failed to issue a refund: {str(e)}. Please contact support."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Cancel the order
        OrderCancellationService.cancel_order(order)

        return Response(
            {"message": f"Order {order_id} has been successfully canceled."},
            status=status.HTTP_200_OK,
        )


# def is_order_eligible_for_return(order):
#     """
#     Check if the order is eligible for return.
#     """
#     if order.delivered_at < timezone.now() + timedelta(days=7):
#         return True, "Order is eligible for return."
#     return False, "Return request is too late."


def process_partial_refund(order, items_to_return):
    """
    Process a partial refund for the selected items in the order.
    """
    # Calculate the total cost of the returned items
    total_cost_of_returned_items = sum(item.get_cost() for item in items_to_return)

    # Calculate the refund amount based on the percentage
    refund_amount = total_cost_of_returned_items * REFUND_PERCENTAGE / 100
    order.refund.refund_amount = refund_amount
    order.save()

    try:
        # Issue the refund
        refund_result = RefundProcessor.process_refund(order)
        if refund_result:
            if order.payment_method == PaymentGateway.PAYSTACK:
                return Response(
                    {
                        "status": refund_result.get("status"),
                        "message": refund_result.get("message"),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(refund_result)
    except Exception as e:
        raise Exception(f"Failed to issue a refund: {str(e)}")


class ReturnValidator:
    @staticmethod
    def validate_return_request(order, items_to_return):
        """
        Validate the return request.
        """

        # Check if the order is eligible for return
        if order.shipping_status != ShippingStatus.DELIVERED:
            return Response(
                {"error": "This order is not eligible for a return."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if the return window has passed
        if order.delivered_at < timezone.now() - timedelta(days=7):
            return Response(
                {"error": "Return request is too late. The return window has expired."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate the items to return
        for item_id in items_to_return:
            try:
                order_item = order.items.get(id=item_id)
                if order_item.returned:
                    return Response(
                        {"error": f"Item {item_id} has already been returned."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except OrderItem.DoesNotExist:
                return Response(
                    {"error": f"Item {item_id} does not belong to this order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # If all checks pass, return None to indicate success
        return None


class ReturnService:
    @staticmethod
    def process_return(order, validated_data, return_obj):
        """
        Process the return request, including marking items as returned,
        and issuing refunds.
        """
        # if items are in good shape admin will manually restock it
        items_to_return_ids = validated_data["items_to_return"]
        partial_refund = validated_data.get("partial_refund", False)
        items_to_return = order.items.filter(id__in=items_to_return_ids)

        # Handle partial refund
        if partial_refund:
            process_partial_refund(order, items_to_return)

        # Handle full refund if return is confirmed
        if return_obj.tracking_number:
            # handle refund only when tracking number is confirmed to be valid
            # refund_result = RefundProcessor.process_refund(order)
            pass

        return {"message": "Return request processed successfully."}


class ReturnRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Request a return for an order",
        description="Allows a user to request a return for a delivered order.",
        tags=tags,
        # responses={
        #     200: OpenApiResponse(description="Return request successful"),
        #     400: OpenApiResponse(description="Invalid request"),
        #     403: OpenApiResponse(description="Not authorized"),
        #     404: OpenApiResponse(description="Order not found"),
        # },
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
            
        ReturnValidator.validate_return_request(order, items_to_return)
        
        # Validate and process the return request
        serializer = ReturnRequestSerializer(data=request.data, context={"order": order})
        serializer.is_valid(raise_exception=True)
        
        # Create the Return object
        return_obj = serializer.save()

        # Process the return using the service class
        result = ReturnService.process_return(order, return_obj, serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)

# path("<uuid:order_id>/cancel/", views.CancelOrderAPIView.as_view()),

def success_response(data, message="Success"):
    return {"status": "success", "message": message, "data": data}

def error_response(message="Error", status_code=400):
    return {"status": "error", "message": message, "status_code": status_code}