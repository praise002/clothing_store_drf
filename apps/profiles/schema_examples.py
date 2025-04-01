from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.schema_examples import (
    DATETIME_EXAMPLE,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
)
from apps.common.serializers import ErrorDataResponseSerializer

PROFILE_EXAMPLE = {
    "user": {
        "id": UUID_EXAMPLE,
        "email": "bob123@example.com",
        "first_name": "Bob",
        "last_name": "Doe",
    },
    "last_updated": DATETIME_EXAMPLE,
    "avatar_url": "https://bobdoeavatar.com",
}


PROFILE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
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
        response=RESPONSE_TYPE,
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

