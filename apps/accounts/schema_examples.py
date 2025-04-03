from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.common.errors import ErrorCode
from apps.common.schema_examples import ERR_RESPONSE_STATUS
from apps.common.serializers import ErrorResponseSerializer

UNAUTHORIZED_USER_RESPONSE = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Unauthorized User or Invalid Access Token",
    examples=[
        OpenApiExample(
            name="Unauthorized User",
            value={
                "status": ERR_RESPONSE_STATUS,
                "message": "Authentication credentials were not provided.",
                "err_code": ErrorCode.UNAUTHORIZED,
            },
        ),
        OpenApiExample(
            name="Invalid Access Token",
            value={
                "status": ERR_RESPONSE_STATUS,
                "message": "Access Token is Invalid or Expired!",
                "err_code": ErrorCode.INVALID_TOKEN,
            },
        ),
    ],
)
