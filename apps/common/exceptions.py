from http import HTTPStatus
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    ValidationError,
    APIException,
    NotFound,
    PermissionDenied,
)

from apps.common.errors import ErrorCode
from apps.common.responses import CustomResponse

import logging

logger = logging.getLogger(__name__)


class RequestError(APIException):
    default_detail = "An error occured"

    def __init__(
        self, err_msg: str, err_code: str, status_code: int = 400, data: dict = None
    ):
        """
        Initialize a RequestError instance.

        Args:
            err_msg (str): The error message.
            err_code (str): The error code.
            status_code (int, optional): The HTTP status code. Defaults to 400.
            data (dict, optional): Additional data related to the error. Defaults to None.
        """
        self.status_code = HTTPStatus(status_code)
        self.err_msg = err_msg
        self.err_code = err_code
        self.data = data

        super().__init__()


class NotFoundError(RequestError):
    def __init__(
        self,
        err_msg: str,
        err_code: str = ErrorCode.NON_EXISTENT,
        status_code: int = 404,
        data: dict = None,
    ):
        super().__init__(err_msg, err_code, status_code, data)


class ValidationErr(RequestError):
    def __init__(
        self,
        field: str,
        message: str,
        err_msg: str = "Validation error",
        err_code: str = ErrorCode.VALIDATION_ERROR,
        status_code: int = 422,
    ):
        data = {field: message}
        super().__init__(err_msg, err_code, status_code, data)


def handle_authentication_failed(exc):
    exc_list = str(exc).split("DETAIL: ")
    print(exc_list)
    return CustomResponse.error(
        message=exc_list[-1],
        err_code=ErrorCode.UNAUTHORIZED,
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def handle_not_authenticated(exc):
    exc_list = str(exc).split("DETAIL: ")
    print(exc_list)
    return CustomResponse.error(
        message=exc_list[-1],
        err_code=ErrorCode.UNAUTHORIZED,
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def handle_request_error(exc):
    return CustomResponse.error(
        message=exc.err_msg,
        err_code=exc.err_code,
        data=exc.data,
        status_code=exc.status_code,
    )


def handle_permission_error(exc):
    exc_list = str(exc).split("DETAIL: ")
    print(exc_list)
    return CustomResponse.error(
        message=exc_list[-1],
        err_code=ErrorCode.UNAUTHORIZED,
        status_code=HTTPStatus.FORBIDDEN,
    )


def handle_not_found_error(exc):
    exc_list = str(exc).split("DETAIL: ")
    print(exc_list)
    return CustomResponse.error(
        message=exc_list[-1],
        err_code=ErrorCode.NON_EXISTENT,
        status_code=HTTPStatus.NOT_FOUND,
    )


def handle_validation_error(exc):
    def extract_errors(detail):
        errors = {}
        for key, value in detail.items():
            if isinstance(value, dict):
                # Recursively process nested fields
                errors[key] = extract_errors(value)
            elif isinstance(value, list):
                errors[key] = str(value[0]).strip() if value else "Unknown error"
            elif isinstance(value, str):
                errors[key] = value.strip()
            else:
                # Handle unexpected types gracefully
                errors[key] = "Unexpected error"

        return errors

    # Log the raw validation errors for debugging
    logger.debug(f"Validation error details: {exc.detail}")

    # Extract and structure the errors
    errors = extract_errors(exc.detail)

    return CustomResponse.error(
        message="Validation error",
        err_code=ErrorCode.VALIDATION_ERROR,
        data=errors,
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )


def handle_invalid_token(exc):
    """
    Handle cases where the JWT token is invalid or expired.
    """
    logger.debug(f"Invalid token error: {exc}")
    return CustomResponse.error(
        message="Access Token is Invalid or Expired!",
        err_code=ErrorCode.INVALID_TOKEN,
        status_code=HTTPStatus.UNAUTHORIZED,
    )


def custom_exception_handler(exc, context):
    try:
        if isinstance(exc, AuthenticationFailed):
            if hasattr(exc, "detail") and (
                "token_not_valid" in str(exc.detail)
                or "Token is invalid or expired" in str(exc.detail)
            ):
                return handle_invalid_token(exc)

            return handle_authentication_failed(exc)
        elif isinstance(exc, NotAuthenticated):
            return handle_not_authenticated(exc)
        elif isinstance(exc, PermissionDenied):
            return handle_permission_error(exc)
        elif isinstance(exc, NotFound):
            return handle_not_found_error(exc)
        elif isinstance(exc, ValidationError):
            return handle_validation_error(exc)
        else:
            status_code = 500 if not hasattr(exc, "status_code") else exc.status_code
            return CustomResponse.error(
                message="Something went wrong!",
                status_code=status_code,
                err_code=ErrorCode.SERVER_ERROR,
            )
    except APIException:
        return CustomResponse.error(
            message="Server error", status_code=500, err_code=ErrorCode.SERVER_ERROR
        )
