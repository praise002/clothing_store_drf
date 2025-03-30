from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.common.errors import ErrorCode
from apps.common.schema_examples import ERR_RESPONSE_STATUS, RESPONSE_TYPE

UNAUTHORIZED_USER_RESPONSE = OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Unauthorized User or Invalid Access Token",
        examples=[
            OpenApiExample(
                name="Unauthorized User",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Authentication credentials were not provided.",
                    "code": ErrorCode.UNAUTHORIZED,
                },
            ),
            OpenApiExample(
                name="Invalid Access Token",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Access Token is Invalid or Expired!",
                    "code": ErrorCode.INVALID_TOKEN,
                },
            ),
        ],
    ),