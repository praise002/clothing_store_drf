from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.cart import Cart
from apps.cart.schema_examples import (
    CART_ADD_UPDATE_RESPONSE,
    CART_LIST_RESPONSE,
    CART_REMOVE_RESPONSE,
)
from apps.common.exceptions import NotFoundError
from apps.common.responses import CustomResponse
from apps.shop.models import Product

from .serializers import CartAddUpdateSerializer, CartSerializer

tags = ["cart"]


class CartDetailView(APIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve the cart",
        description="This endpoint retrieves the cart.",
        tags=tags,
        responses=CART_LIST_RESPONSE,
    )
    def get(self, request):
        cart = Cart(request)
        serializer = self.serializer_class(cart)
        return CustomResponse.success(
            message="Cart retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class CartAddUpdateView(APIView):
    serializer_class = CartAddUpdateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add or update a product to the cart",
        description="""
        This endpoint adds or updates a product to the cart.
        Set override quantity to True if you want to override the quantity.
        Set override quantity to false which is the default if you want to add
        to the items in the cart.
        """,
        tags=tags,
        responses=CART_ADD_UPDATE_RESPONSE,
    )
    def post(self, request):
        # Use CartAddSerializer for input validation
        # Use CartSerializer for response data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        try:
            product = Product.objects.get(
                id=product_id,
                is_available=True,
                in_stock__gt=0,
            )
        except Product.DoesNotExist:
            raise NotFoundError(
                err_msg="Product not found.",
            )

        cart = Cart(request)
        override_quantity = serializer.validated_data["override"]
        cart.add(
            product=product,
            quantity=serializer.validated_data["quantity"],
            override_quantity=override_quantity,
        )

        # Serialize response with CartSerializer
        cart_serializer = CartSerializer(cart)
        if override_quantity:
            return CustomResponse.success(
                message="Product updated in cart.",
                data=cart_serializer.data,
                status_code=status.HTTP_200_OK,
            )

        return CustomResponse.success(
            message="Product added to cart.",
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
        responses=CART_REMOVE_RESPONSE,
    )
    def delete(self, request, product_id):
        cart = Cart(request)

        try:
            product = Product.objects.get(
                id=product_id,
            )
        except Product.DoesNotExist:
            raise NotFoundError(
                err_msg="Product not found.",
            )

        if not cart.remove(product):
            raise NotFoundError(
                err_msg="Product not found in cart.",
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_204_NO_CONTENT)
