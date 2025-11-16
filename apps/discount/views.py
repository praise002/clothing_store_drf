from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.errors import ErrorCode
from apps.common.exceptions import NotFoundError
from apps.common.responses import CustomResponse
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.discount.models import Coupon, CouponUsage
from apps.discount.serializers import CouponApplySerializer
from apps.discount.service import apply_coupon_discount_to_order
from apps.orders.choices import PaymentStatus, ShippingStatus
from apps.orders.models.order import Order
from apps.orders.serializers.order import (
    OrderWithDiscountResponseSerializer,
    OrderWithDiscountSerializer,
)
from apps.orders.views import tags


class ApplyCouponView(APIView):
    serializer_class = CouponApplySerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Apply coupon to an order",
        description="This endpoint applies coupon to an order.",
        tags=tags,
        responses={
            200: OrderWithDiscountResponseSerializer,
            404: ErrorResponseSerializer,
            422: ErrorDataResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        # 1. Validate coupon code
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if the order_id is present in the URL
        order_id = kwargs.get("order_id")
        if not order_id:
            raise NotFoundError(err_msg="Order ID is required.")
        # 2. Get order
        try:
            order = (
                Order.objects.select_related("customer")
                .prefetch_related("items")
                .get(id=order_id)
            )
        except Order.DoesNotExist:
            raise NotFoundError(err_msg="Order not found.")

        if (
            order.payment_status == PaymentStatus.SUCCESSFUL
            or order.shipping_status == ShippingStatus.DELIVERED
        ):
            return CustomResponse.error(
                message="This order has already been paid for.",
                err_code=ErrorCode.VALIDATION_ERROR,
            )

        coupon = Coupon.objects.get(code=serializer.validated_data["code"])

        # 3. Validate coupon against order
        coupon_usage = CouponUsage.objects.filter(coupon=coupon, order=order).exists()

        if coupon_usage:
            return CustomResponse.error(
                message="Coupon already applied to order.",
                err_code=ErrorCode.BAD_REQUEST,
            )

        # 4. Apply discount
        apply_coupon_discount_to_order(coupon, order)

        # Refresh order from DB to ensure we have latest data
        order.refresh_from_db()

        # serialize with order
        order_serializer = OrderWithDiscountSerializer(order)
        # 5. Return order details with discount
        return CustomResponse.success(
            message="Coupon applied successfully.",
            data=order_serializer.data,
            status_code=status.HTTP_200_OK,
        )
