from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.common.schema_examples import RESPONSE_TYPE, SUCCESS_RESPONSE_STATUS
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer

PROFILE_EXAMPLE = {
    "user": {
        "first_name": "John",
        "last_name": "Doe",
    },
    "avatar_url": "https://johndoeavatar.com",
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
                    "message": "Profile updated successfully",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
    401: ErrorResponseSerializer,
}
