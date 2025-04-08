from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.errors import ErrorCode
from apps.common.schema_examples import (
    AVATAR_URL,
    DATETIME_EXAMPLE,
    ERR_RESPONSE_STATUS,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer
from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer

PROFILE_EXAMPLE = {
    "user": {
        "id": UUID_EXAMPLE,
        "email": "bob123@example.com",
        "first_name": "Bob",
        "last_name": "Doe",
    },
    "last_updated": DATETIME_EXAMPLE,
    "avatar_url": AVATAR_URL,
}

SHIPPING_ADDRESS_EXAMPLE_1 = [
    {
        "id": UUID_EXAMPLE,
        "user": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
        "phone_number": "0xxxxxxxxxx",
        "state": "Abia",
        "postal_code": "12345",
        "city": "Umahia",
        "street_address": "24, Aba Road",
        "shipping_fee": 5000,
        "shipping_time": "1-3 business days",
        "default": "true",
    },
]


SHIPPING_ADDRESS_EXAMPLE_2 = [
    {
        "id": UUID_EXAMPLE,
        "user": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
        "phone_number": "0xxxxxxxxxx",
        "state": "Abia",
        "postal_code": "12345",
        "city": "Umahia",
        "street_address": "24, Aba Road",
        "shipping_fee": 0,
        "shipping_time": "1-3 business days",
        "default": "true",
    },
    {
        "id": UUID_EXAMPLE,
        "user": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
        "phone_number": "0xxxxxxxxxx",
        "state": "Abia",
        "postal_code": "12345",
        "city": "Umahia",
        "street_address": "24, Aba Road",
        "shipping_fee": 0,
        "shipping_time": "1-3 business days",
        "default": "false",
    },
]


SHIPPING_ADDRESS_EXAMPLE_3 = [
    {
        "id": UUID_EXAMPLE,
        "user": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
        "phone_number": "0xxxxxxxxxx",
        "state": "Abia",
        "postal_code": "12345",
        "city": "Umahia",
        "street_address": "24, Aba Road",
        "shipping_fee": 5000,
        "shipping_time": "1-3 business days",
        "default": "false",
    },
]


PROFILE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=ProfileSerializer,
        description="Profile Update Successful",
        examples=[
            OpenApiExample(
                name="Profile Update Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile updated successfully.",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    401: UNAUTHORIZED_USER_RESPONSE,
}

PROFILE_RETRIEVE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Profile Retrieve Successful",
        response=ProfileSerializer,
        examples=[
            OpenApiExample(
                name="Profile Retrieve Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Profile retrieved successfully.",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}


def build_avatar_request_schema():
    return {
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "avatar": {
                    "type": "string",
                    "format": "binary",
                    "description": "Profile image file",
                },
            },
            "required": ["avatar"],
        }
    }


SHIPPING_ADDRESS_RESPONSE_EXAMPLE = OpenApiResponse(
    description="Shipping Address Retrieve Successful",
    response=ShippingAddressSerializer,
    examples=[
        OpenApiExample(
            name="Shipping Address Retrieve Successful",
            value={
                "status": SUCCESS_RESPONSE_STATUS,
                "message": "Shipping addresses retrieved successfully.",
                "data": SHIPPING_ADDRESS_EXAMPLE_1,
            },
        ),
        OpenApiExample(
            name="Shipping Address Retrieve Successful with multiple addresses",
            value={
                "status": SUCCESS_RESPONSE_STATUS,
                "message": "Shipping addresses retrieved successfully.",
                "data": SHIPPING_ADDRESS_EXAMPLE_2,
            },
        ),
    ],
)

SHIPPING_ADDRESS_RETRIEVE_RESPONSE_EXAMPLE = {
    200: SHIPPING_ADDRESS_RESPONSE_EXAMPLE,
    401: UNAUTHORIZED_USER_RESPONSE,
}

SHIPPING_ADDRESS_CREATE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        description="Shipping Address Retrieve Successful",
        response=ShippingAddressSerializer,
        examples=[
            OpenApiExample(
                name="Shipping Address Retrieve Successful Example 1",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address created successfully.",
                    "data": SHIPPING_ADDRESS_EXAMPLE_1,
                },
            ),
            OpenApiExample(
                name="Shipping Address Retrieve Successful Example 2",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address created successfully.",
                    "data": SHIPPING_ADDRESS_EXAMPLE_3,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    401: UNAUTHORIZED_USER_RESPONSE,
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation error",
        examples=[
            OpenApiExample(
                name="Validation error",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Validation error",
                    "code": ErrorCode.VALIDATION_ERROR,
                    "data": {
                        "state": '"abia" is not a valid choice.',
                    },
                },
            ),
        ],
    ),
}


SHIPPING_ADDRESS_DETAIL_GET_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Shipping Address Retrieve Successful",
        response=ShippingAddressSerializer,
        examples=[
            OpenApiExample(
                name="Shipping Address Retrieve Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address retrieved successfully.",
                    "data": SHIPPING_ADDRESS_EXAMPLE_3,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Shipping address not found",
        examples=[
            OpenApiExample(
                name="Shipping address not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Shipping address not found",
                    "err_code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

SHIPPING_ADDRESS_DETAIL_PATCH_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        description="Shipping Address Update Successful",
        response=ShippingAddressSerializer,
        examples=[
            OpenApiExample(
                name="Shipping Address Update Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address updated successfully.",
                    "data": SHIPPING_ADDRESS_EXAMPLE_1,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    401: UNAUTHORIZED_USER_RESPONSE,
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Shipping address not found",
        examples=[
            OpenApiExample(
                name="Shipping address not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Shipping address not found",
                    "err_code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

SHIPPING_ADDRESS_DETAIL_DELETE_RESPONSE_EXAMPLE = {
    204: None,
    401: UNAUTHORIZED_USER_RESPONSE,
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Cannot delete default shipping address",
        examples=[
            OpenApiExample(
                name="Cannot delete default shipping address",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Cannot delete default shipping address",
                    "err_code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    404: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Shipping address not found",
        examples=[
            OpenApiExample(
                name="Shipping address not found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Shipping address not found.",
                    "err_code": ErrorCode.NON_EXISTENT,
                },
            ),
        ],
    ),
}

# {
#   "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1MTc0NjY5MCwiaWF0IjoxNzQzOTcwNjkwLCJqdGkiOiJiMzc2YWM4NGZlMTM0MzQ5OGM4MTg4ODhlY2E4ZDIxYSIsInVzZXJfaWQiOiI3ZTc3YmJkMS01MmI0LTQzMzMtYjRhYi04NzVjYjA4MzkxYzQiLCJmdWxsX25hbWUiOiJQcmFpc2UgSUQifQ.sF5n0uNyXVQAzd661axaE2QPzcvwhI7BjgxdxzcDtxY",
#   "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0MDU3MDkwLCJpYXQiOjE3NDM5NzA2OTAsImp0aSI6IjdmOGY5MGY5NjRmYzQxMTdhZjIxNzhjYTU4MWVhYTBkIiwidXNlcl9pZCI6IjdlNzdiYmQxLTUyYjQtNDMzMy1iNGFiLTg3NWNiMDgzOTFjNCIsImZ1bGxfbmFtZSI6IlByYWlzZSBJRCJ9.ydcC1Op4wdq7UJzQlCV8zO0COyT2anEC-S9wep5lo1k"
# }