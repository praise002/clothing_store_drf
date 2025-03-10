from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse


from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)


from apps.orders.choices import PaymentGateway, PaymentStatus, ShippingStatus
from apps.orders.models import Order
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)
from apps.orders.tasks import order_created
from apps.payments.utils import issue_refund


tags = ["orders"]


# TODO: SHIPPING ADDRESS ASSOCIATED WITH AN ORDER CANNOT BE CHANGED AFTER ORDER IS PLACED
# DYNAMICALLY GET THE SHIPPING FEE AND SAVE IT TO THE ORDER
class OrderCreateView(APIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create an order",
        description="This endpoint creates an order from the user's cart and assigns a shipping address.",
        tags=tags,
        responses={
            201: OrderSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        # Validate the input data
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Save the order using the serializer
        order = serializer.save()

        # Serialize the created order for the response
        order_serializer = OrderSerializer(order)

        # launch asynchronous task
        order_created.delay(order.id)

        return Response(
            {
                "message": "Order created successfully. Shipping address associated with this order will remain the same even if updated.",
                "data": order_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderCreateGenericView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create an order",
        description="This endpoint creates an order from the user's cart and assigns a shipping address.",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Override the create method to customize the response format.
        """
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        order = serializer.instance
        order_serializer = OrderSerializer(order)

        # launch asynchronous task
        order_created.delay(order.id)

        return Response(
            {
                "message": "Order created successfully.",
                "data": order_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderHistoryView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve the order history of the authenticated user",
        description="This endpoint retrieves all orders placed by the authenticated user.",
        tags=tags,
        responses={
            200: OrderSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        """
        Retrieve the order history of the authenticated user.
        """
        # Get the authenticated user's profile
        user_profile = request.user.profile

        # Retrieve all orders for the user
        orders = Order.objects.filter(customer=user_profile).order_by("-created")

        if not orders.exists():
            return Response(
                {"message": "No orders found in your history."},
                status=status.HTTP_200_OK,
            )

        # Serialize the orders
        serializer = self.serializer_class(orders, many=True)

        # Return the serialized data
        return Response(
            {
                "message": "Order history retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

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
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the order can be canceled
        if order.shipping_status == ShippingStatus.IN_TRANSIT:
            return Response(
                {
                    "error": "This order cannot be canceled as it is already in transit."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if order.shipping_status == ShippingStatus.DELIVERED:
            pass
        
        return None

class RefundProcessor:
    @staticmethod
    def process_refund(order):
        if order.payment_status == PaymentStatus.SUCCESSFUL:
            try:
                refund_result = issue_refund(
                    order.payment_method, order.tx_ref, order.transaction_id
                )
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

        if order.customer.user != request.user:
            return Response(
                {"error": "Not authorized to cancel this order"},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        # Check if the order is already canceled
        if order.shipping_status == ShippingStatus.CANCELLED:
            return Response(
                {"error": "This order has already been canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the order can be canceled
        if order.shipping_status == ShippingStatus.IN_TRANSIT:
            return Response(
                {
                    "error": "This order cannot be canceled as it is already in transit."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if order.shipping_status == ShippingStatus.DELIVERED:
            pass

        # Issue a refund if the payment was successful
        if order.payment_status == PaymentStatus.SUCCESSFUL:
            try:
                refund_result = issue_refund(
                    order.payment_method, order.tx_ref, order.transaction_id
                )
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

        order.shipping_status = ShippingStatus.CANCELLED
        order.save()

        # Restore stock for each order item
        for item in order.items.all():
            product = item.product
            product.in_stock += item.quantity
            product.save()

        return Response(
            {"message": f"Order {order_id} has been successfully canceled."},
            status=status.HTTP_200_OK,
        )

# TODO: REWORK ON THE SCHEMA DOCS TO SMTIN MORE READABLE AND UNDERSTANDABLE
# FIXME: PENDING ORDRES NOT RECEIVED EMAILS