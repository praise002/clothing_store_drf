from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
)

from apps.accounts.serializers import CustomTokenObtainPairSerializer, RegisterSerializer
from apps.common.errors import ErrorCode
from apps.common.schema_examples import ACCESS_TOKEN, ERR_RESPONSE_STATUS, REFRESH_TOKEN, SUCCESS_RESPONSE_STATUS
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer

REGISTER_EXAMPLE = {
  "email": "bob123@example.com"
}

LOGIN_EXAMPLE = {
    "refresh": REFRESH_TOKEN,
    "access": ACCESS_TOKEN,
}

REGISTER_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        response=RegisterSerializer,
        description="OTP Sent Successful",
        examples=[
            OpenApiExample(
                name="OTP Sent Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "OTP sent for email verification.",
                    "data": REGISTER_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
}

LOGIN_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=CustomTokenObtainPairSerializer,
        description="Login Successful",
        examples=[
            OpenApiExample(
                name="Login Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Login successful.",
                    "data": LOGIN_EXAMPLE,
                },
            ),
        ],
    ),
    400: ErrorDataResponseSerializer,
}

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

# {
#   "status": "failure",
#   "message": "No active account found with the given credentials",
#   "code": "unauthorized"
# }

# {
#   "status": "failure",
#   "message": "Validation error",
#   "code": "validation_error",
#   "data": {
#     "password": "This field may not be blank."
#   }
# }

# {
#   "status": "failure",
#   "message": "Invalid email or password.",
#   "code": "non_existent"
# }