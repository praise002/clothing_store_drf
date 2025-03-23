from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from apps.cart.cart import Cart
from apps.common.responses import CustomResponse
from apps.common.serializers import (
    ErrorResponseSerializer,
)
from drf_spectacular.utils import extend_schema
from apps.shop.models import Product

from .serializers import CartResponseSerializer, CartSerializer, CartAddUpdateSerializer

tags = ["cart"]


class CartDetailView(APIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve the cart",
        description="This endpoint retrieves the cart.",
        tags=tags,
        responses={
            200: CartResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        cart = Cart(request)
        serializer = self.serializer_class(cart)
        return CustomResponse.success(
            message="Cart retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class CartAddUpdateView(APIView):
    serializer_class = CartAddUpdateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add or update a product to the cart",
        description="This endpoint adds or updates a product to the cart.",
        tags=tags,
        responses={
            200: CartResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        # Use CartAddSerializer for input validation
        # Use CartSerializer for response data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        product = get_object_or_404(
            Product,
            id=product_id,
            is_available=True,
            in_stock__gt=0,
        )

        cart = Cart(request)
        cart.add(
            product=product,
            quantity=serializer.validated_data["quantity"],
            override_quantity=serializer.validated_data["override"],
        )

        # Serialize response with CartSerializer
        cart_serializer = CartSerializer(cart)
        return CustomResponse.success(
            message="Product added to cart",
            data=cart_serializer.data,
            status_code=status.HTTP_200_OK,
        )


class CartRemoveView(APIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Remove a product from the cart",
        description="This endpoint removes a product from the cart.",
        tags=tags,
        responses={
            200: CartResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, product_id):
        cart = Cart(request)

        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        cart_serializer = self.serializer_class(cart)
        return CustomResponse.success(
            message="Product removed from cart",
            data=cart_serializer.data,
            status_code=status.HTTP_200_OK,
        )
