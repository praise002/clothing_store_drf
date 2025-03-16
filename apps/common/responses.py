from rest_framework.response import Response


class CustomResponse:
    @staticmethod
    def success(message, data=None, status_code=200):
        """
        Returns a standardized success response.
        :param message: A human-readable success message.
        :param data: Optional data to include in the response.
        :param status: HTTP status code (default: 200).
        :return: DRF Response object.
        """
        response = {
            "status": "success",
            "message": message,
        }
        if data is not None:
            response["data"] = data
        return Response(data=response, status=status_code)

    @staticmethod
    def error(message, status_code=400):
        """
        Returns a standardized error response.
        :param message: A human-readable error message.
        :param error_code: Optional error code for machine-readable identification.
        :param status: HTTP status code (default: 400).
        :return: DRF Response object.
        """
        response = {
            "status": "failure",
            "message": message,
            # "code": err_code, #TODO: LATER
        }

        return Response(data=response, status=status_code)
