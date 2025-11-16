from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.common.schema_examples import (
    AVATAR_URL,
    ERR_RESPONSE_STATUS,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.shop.serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    WishlistSerializer,
)


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
            "image_url": AVATAR_URL,
            "cropped_image_url": AVATAR_URL,
        }
    ],
}

REVIEW_EXAMPLE = {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "product": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "customer": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "text": "I love it.",
    "rating": 5,
    "image": AVATAR_URL,
    "created": "2025-05-04T17:25:10.464Z",
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
                    "message": "Products retrieved successfully.",
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
                    "message": "Products retrieved successfully.",
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

WISHLIST_RESPONSE = {
    # 200: WishlistResponseSerializer,
    200: OpenApiResponse(
        response=WishlistSerializer,
        description="Products Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Wishlist retrieved successfully.",
                    "data": WISHLIST_EXAMPLE,
                },
            ),
        ],
    ),
    401: ErrorResponseSerializer,
}

WISHLIST_ADD_PRODUCT_RESPONSE = {
    200: OpenApiResponse(
        response=WishlistSerializer,
        description="Product Added to Wishlist",
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
    409: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Product Exist in Wishlist",
        examples=[
            OpenApiExample(
                name="Already Exists Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Product already in wishlist.",
                    "code": "already_exists",
                },
            ),
        ],
    ),
}

WISHLIST_REMOVE_PRODUCT_RESPONSE = {
    200: OpenApiResponse(
        response=WishlistSerializer,
        description="Product Removed from Wishlist",
        examples=[
            OpenApiExample(
                name="Remove from Wishlist",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product removed from wishlist.",
                },
            ),
        ],
    ),
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
    422: ErrorResponseSerializer,
}

REVIEW_CREATE_RESPONSE = {
    # 201: ReviewResponseSerializer,
    201: OpenApiResponse(
        response=ReviewSerializer,
        description="Review Created",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Review created successfully.",
                    "data": REVIEW_EXAMPLE,
                },
            ),
        ],
    ),
    401: ErrorResponseSerializer,
    404: ErrorResponseSerializer,
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

REVIEW_UPDATE_RESPONSE = {
    # 200: ReviewResponseSerializer,
    200: OpenApiResponse(
        response=ReviewSerializer,
        description="Review Updated",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Review updated successfully.",
                    "data": REVIEW_EXAMPLE,
                },
            ),
        ],
    ),
    
    401: ErrorResponseSerializer,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
        examples=[
            OpenApiExample(
                name="Permission Denied Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You don't have permission to update this review.",
                    "code": "forbidden",
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Review Does Not Exist",
        examples=[
            OpenApiExample(
                name="Non-existent Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Review not found.",
                    "code": "non_existent",
                },
            ),
        ],
    ),
    422: ErrorDataResponseSerializer,
}

REVIEW_DELETE_RESPONSE = {
    204: None,
    401: ErrorResponseSerializer,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
        examples=[
            OpenApiExample(
                name="Permission Denied Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "You don't have permission to delete this review.",
                    "code": "forbidden",
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Review Does Not Exist",
        examples=[
            OpenApiExample(
                name="Non-existent Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Review not found.",
                    "code": "non_existent",
                },
            ),
        ],
    ),
}
