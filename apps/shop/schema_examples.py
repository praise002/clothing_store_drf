from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.common.schema_examples import (
    AVATAR_URL,
    ERR_RESPONSE_STATUS,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.shop.serializers import (
    CategorySerializer,
    ProductSerializer,
    WishlistSerializer,
)

# "status": SUCCESS_RESPONSE_STATUS,
# "message": "Paginated data retrieved successfully.",
CATEGORY_EXAMPLE = [
    {
        "id": "5cb41be0-c5e0-4081-a354-6b04f74444b2",
        "name": "Textiles",
        "slug": "textiles",
    },
    {
        "id": "eadcecaf-9306-492c-9a94-d9c2c84c9720",
        "name": "Gadgets",
        "slug": "gadgets",
    },
    {
        "id": "0108edb4-9219-4d49-979d-d34960d4bdb8",
        "name": "Female dresses",
        "slug": "female-dresses",
    },
]

PRODUCT_EXAMPLE = [
    {
        "id": "3e06dbc0-71a3-4a0d-95ba-3110d01f8f76",
        "name": "Jumpsuit",
        "slug": "jumpsuit",
        "description": "Test",
        "category": {
            "id": "0108edb4-9219-4d49-979d-d34960d4bdb8",
            "name": "Female dresses",
            "slug": "female-dresses",
        },
        "price": "5000.00",
        "in_stock": 18,
        "is_available": "true",
        "featured": "false",
        "flash_deals": "false",
        "avg_rating": 0,
        "image_url": AVATAR_URL,
        "cropped_image_url": AVATAR_URL,
    }
]

PRODUCT_REVIEWS_EXAMPLE = [
    {
        "id": "3e06dbc0-71a3-4a0d-95ba-3110d01f8f76",
        "name": "Jumpsuit",
        "slug": "jumpsuit",
        "description": "Test",
        "category": {
            "id": "0108edb4-9219-4d49-979d-d34960d4bdb8",
            "name": "Female dresses",
            "slug": "female-dresses",
        },
        "price": "5000.00",
        "in_stock": 18,
        "is_available": "true",
        "featured": "false",
        "flash_deals": "false",
        "avg_rating": 0,
        "image_url": AVATAR_URL,
        "cropped_image_url": AVATAR_URL,
        "reviews": [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "product": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "customer": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "text": "string",
                "rating": 5,
                "image": "string",
                "created": "2025-05-04T01:28:09.133Z",
            }
        ],
    },
]


WISHLIST_EXAMPLE = {
    "data": {
        "id": UUID_EXAMPLE,
        "profile": "827ad08b-0120-4e1f-90b5-653291bfc82a",
        "products": [
            {
                "id": "2fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Product 1",
                "slug": "blue-gown",
                "description": "A description of product 1",
                "category": {
                    "id": "827ad08b-0120-4e1f-90b5-653291bfc81a",
                    "name": "Category 1",
                    "slug": "female-wears",
                },
                "price": "30.00",
                "in_stock": 5,
                "is_available": True,
                "featured": True,
                "flash_deals": True,
                "avg_rating": 0,
                "image_url": "http://res.cloudinary.com/dq0ow9lxw/image/upload/v1739892397/products/s2afqlfaacpt9gpu1xdt.jpg",
                "cropped_image_url": "http://res.cloudinary.com/dq0ow9lxw/image/upload/c_fill,g_auto,h_250,w_250/v1/products/s2afqlfaacpt9gpu1xdt",
            }
        ],
    }
}

CATEGORY_LIST_RESPONSE = {
    # 200: CategoryResponseSerializer,
    200: OpenApiResponse(
        response=CategorySerializer,
        description="Categories Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "data": CATEGORY_EXAMPLE,
                },
            ),
        ],
    ),
}

CATEGORY_PRODUCT_LIST_RESPONSE = {
    # 200: ProductResponseSerializer,
    # 404: ErrorResponseSerializer,
    200: OpenApiResponse(
        response=ProductSerializer,
        description="Products Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "data": PRODUCT_EXAMPLE,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Category Does Not Exist",
        examples=[
            OpenApiExample(
                name="Non-existent Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Category does not exist.",
                    "code": "non_existent",
                },
            ),
        ],
    ),
}

PRODUCT_LIST_RESPONSE = {
    # 200: ProductResponseSerializer,
    200: OpenApiResponse(
        response=ProductSerializer,
        description="Products Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Product not found.",
                    "data": PRODUCT_EXAMPLE,
                },
            ),
        ],
    ),
}

PRODUCT_RETRIEVE_RESPONSE = {
    # 200: ProductResponseSerializer,
    # 404: ErrorResponseSerializer,
    200: OpenApiResponse(
        response=ProductSerializer,
        description="Product Details Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "data": PRODUCT_EXAMPLE,
                },
            ),
        ],
    ),
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

PRODUCT_REVIEW_RETRIEVE_RESPONSE = {
    # 200: ProductResponseSerializer,
    # 404: ErrorResponseSerializer,
    200: OpenApiResponse(
        response=ProductSerializer,
        description="Product Details Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "success": SUCCESS_RESPONSE_STATUS,
                    "message": "Product retrieved successfully.",
                    "data": PRODUCT_EXAMPLE,
                },
            ),
        ],
    ),
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

WISHLIST_ADD_PRODUCT_RESPONSE = {
    200: OpenApiResponse(
        response=WishlistSerializer,
        examples=[
            OpenApiExample(
                name="Add to Wishlist",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product added to wishlist",
                    "data": WISHLIST_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    404: ErrorResponseSerializer,
    409: ErrorResponseSerializer,
    401: ErrorResponseSerializer,
}

WISHLIST_REMOVE_PRODUCT_RESPONSE = {
    200: OpenApiResponse(
        response=WishlistSerializer,
        examples=[
            OpenApiExample(
                name="Remove from Wishlist",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product removed from wishlist",
                },
            ),
        ],
    ),
    400: ErrorResponseSerializer,
    401: ErrorResponseSerializer,
    404: ErrorDataResponseSerializer,
}
