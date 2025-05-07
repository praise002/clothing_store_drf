from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.cart.serializers import CartSerializer
from apps.common.schema_examples import (
    AVATAR_URL,
    ERR_RESPONSE_STATUS,
    SUCCESS_RESPONSE_STATUS,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer


CART_ITEMS_EXAMPLE = {
    "items": [
        {
            "product": {
                "id": "6a6af0d8-c1be-488e-a196-afaccddbece8",
                "name": "Office wear",
                "slug": "office-wear",
                "description": "Lorem",
                "category": {
                    "id": "0108edb4-9219-4d49-979d-d34960d4bdb8",
                    "name": "Female dresses",
                    "slug": "female-dresses",
                },
                "price": "8000.00",
                "in_stock": 6,
                "is_available": "true",
                "image_url": AVATAR_URL,
                "cropped_image_url": AVATAR_URL,
            },
            "quantity": 1,
            "price": "8000.00",
            "total_price": "8000.00",
        }
    ],
    "total_items": 1,
    "total_price": 8000,
}

CART_LIST_EMPTY_EXAMPLE = {"items": [], "total_items": 0, "total_price": 0}

CART_LIST_EXAMPLE = {
    "items": [
        {
            "product": {
                "id": "6a6af0d8-c1be-488e-a196-afaccddbece8",
                "name": "Office wear",
                "slug": "office-wear",
                "description": "Lorem",
                "category": {
                    "id": "0108edb4-9219-4d49-979d-d34960d4bdb8",
                    "name": "Female dresses",
                    "slug": "female-dresses",
                },
                "price": "8000.00",
                "in_stock": 6,
                "is_available": "true",
                "image_url": AVATAR_URL,
                "cropped_image_url": AVATAR_URL,
            },
            "quantity": 2,
            "price": "8000.00",
            "total_price": "16000.00",
        }
    ],
    "total_items": 2,
    "total_price": 16000,
}


CART_LIST_RESPONSE = {
    # 200: CartResponseSerializer,
    200: OpenApiResponse(
        response=CartSerializer,
        description="Cart Returned",
        examples=[
            OpenApiExample(
                name="Empty Cart Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Cart retrieved successfully.",
                    "data": CART_LIST_EMPTY_EXAMPLE,
                },
            ),
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Cart retrieved successfully.",
                    "data": CART_LIST_EXAMPLE,
                },
            ),
        ],
    ),
    401: ErrorResponseSerializer,
}

CART_ADD_UPDATE_RESPONSE = {
    # 200: CartResponseSerializer,
    # 404: ErrorResponseSerializer,
    200: OpenApiResponse(
        response=CartSerializer,
        description="Cart Added or Updated",
        examples=[
            OpenApiExample(
                name="Success Added Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product added to cart.",
                    "data": CART_ITEMS_EXAMPLE,
                },
            ),
            OpenApiExample(
                name="Success Update Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product updated in cart.",
                    "data": CART_ITEMS_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    401: ErrorResponseSerializer,
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Product Does Not Exist",
        examples=[
            OpenApiExample(
                name="Non-existent Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Product not found.",
                    "code": "non_existent",
                },
            ),
        ],
    ),
}

CART_REMOVE_RESPONSE = {
    204: None,
    400: ErrorDataResponseSerializer,
    401: ErrorResponseSerializer,
    # 404: ErrorResponseSerializer,
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Product Does Not Exist",
        examples=[
            OpenApiExample(
                name="Non-existent Response 1",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Product not found.",
                    "code": "non_existent",
                },
            ),
            OpenApiExample(
                name="Non-existent Response 2",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Product not found in cart.",
                    "code": "non_existent",
                },
            ),
        ],
    ),
}
