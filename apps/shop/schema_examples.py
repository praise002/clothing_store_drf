from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.common.schema_examples import (
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer


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


WISHLIST_ADD_PRODUCT_RESPONSE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
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
        response=RESPONSE_TYPE,
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
