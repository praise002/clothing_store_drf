from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema


from apps.common.responses import CustomResponse
from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
)


from apps.orders.filters import OrderFilter
from apps.orders.models import Order
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)
from apps.orders.serializers.order import OrderResponseSerializer
from apps.orders.tasks import order_created


tags = ["orders"]


class OrderCreateView(APIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create an order",
        description=(
            "Creates a new order from the authenticated user's cart. "
            "A shipping address must be selected, and its details will remain immutable once the order is placed."
        ),
        tags=tags,
        responses={
            201: OrderResponseSerializer,
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
        order, discount_info = serializer.save()

        # Serialize the created order for the response
        order_serializer = OrderSerializer(order)

        # launch asynchronous task
        order_created.delay(order.id)

        return CustomResponse.success(
            message="Order created successfully. Shipping address associated with this order will remain the same even if updated.",
            data={
                "order": order_serializer.data,
                "discount_info": discount_info,
            },
            status_code=status.HTTP_201_CREATED,
        )


class OrderCreateGenericView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create an order",
        description="This endpoint creates an order from the user's cart and assigns a shipping address.",
        tags=tags,
        responses={
            201: OrderResponseSerializer,
            400: ErrorDataResponseSerializer,
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

        return CustomResponse.success(
            message="Order created successfully. Shipping address associated with this order will remain the same even if updated.",
            data=order_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class OrderHistoryView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve the order history of the authenticated user",
        description="This endpoint retrieves all orders placed by the authenticated user.",
        tags=tags,
        responses={
            200: OrderResponseSerializer,
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
            return CustomResponse.success(
                message="No orders found in your history.",
                status_code=status.HTTP_200_OK,
            )

        # Serialize the orders
        serializer = self.serializer_class(orders, many=True)

        # Return the serialized data
        return CustomResponse.success(
            message="Order history retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class OrderHistoryGenericAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_queryset(self):
        """
        Return orders belonging to the authenticated user.
        """

        # Check if this is a schema generation request
        if getattr(self, "swagger_fake_view", False):
            # Return an empty queryset to prevent errors during schema generation
            return Order.objects.none()

        return Order.objects.filter(customer=self.request.user.profile).order_by(
            "-created"
        )

    def list(self, request, *args, **kwargs):
        """
        Override the list method to customize the response format.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if not queryset.exists():
            return CustomResponse.success(
                message="No orders found in your history.",
                status_code=status.HTTP_200_OK,
            )

        return CustomResponse.success(
            message="Order history retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Retrieve Order History",
        description=(
            "Retrieves all orders placed by the authenticated user, sorted by creation date in descending order. "
            "Supports filtering by shipping status."
        ),
        tags=tags,
        responses={
            200: OrderResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        """
        Retrieve the order history of the authenticated user.
        """
        return super().get(request)
