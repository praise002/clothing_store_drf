from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.cart.cart import Cart
from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)

# from apps.common.validators import validate_uuid
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)
from apps.profiles.models import ShippingAddress

tags = ["orders"]


# TODO: SHIPPING ADDRESS ASSOCIATED WITH AN ORDER CANNOT BE CHANGED AFTER ORDER IS PLACED
# DYNAMICALLY GET THE SHIPPING FEE AND SAVE IT TO THE ORDER
class OrderCreateView(APIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create_order_with_items(self, cart, shipping_address, user):
        # Create the order
        order = Order.objects.create(
            customer=user.profile,
            shipping_address=shipping_address,
        )

        # Add items from the cart to the order
        for item in cart:
            product = item["product"]
            quantity = item["quantity"]
            price = Decimal(item["price"])

            # Check if enough stock available
            if product.in_stock < quantity:
                raise ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.in_stock}"
                )

            # Create order item and reduce stock
            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=price
            )

            # Update product stock
            product.in_stock -= quantity
            product.save()
            
        return order

    @extend_schema(
        summary="Create an order",
        description="This endpoint creates an order from the user's cart and assigns a shipping address.",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        # Validate the input data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        shipping_id = serializer.validated_data.get("shipping_id")

        try:
            # Ensure the cart exists in Redis
            cart = Cart(request)
            if not cart.cart:  # falsy evaluates to true if cart is empty
                return Response(
                    {"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure the shipping address exists and belongs to the user
            shipping_address = ShippingAddress.objects.get(
                id=shipping_id, user=request.user.profile
            )
            
            with transaction.atomic():
                order = self.create_order_with_items(
                    cart=cart,
                    shipping_address=shipping_address,
                    user=request.user
                )

            # Clear the cart after creating the order
            cart.clear()

            order_serializer = OrderSerializer(order)

            # Return success response
            return Response(
                {
                    "message": "Order created successfully.",
                    "data": order_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except ShippingAddress.DoesNotExist:
            return Response(
                {"error": "Shipping address not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {
                    "error": "An error occurred while creating the order.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
