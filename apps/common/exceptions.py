from http import HTTPStatus
from rest_framework.exceptions import (
    AuthenticationFailed,
    ValidationError,
    APIException,
)


class RequestError(APIException):
    def __init__(self, err_msg: str, err_code: str, status_code: int=400, data: dict = None):
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
