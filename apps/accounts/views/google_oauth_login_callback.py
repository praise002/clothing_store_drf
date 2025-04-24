from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status

from drf_spectacular.utils import extend_schema

from apps.accounts.models import User
from apps.accounts.utils import google_callback
from apps.common.errors import ErrorCode
from apps.common.responses import CustomResponse
from apps.common.serializers import (
    ErrorDataResponseSerializer,
    SuccessResponseSerializer,
)

from .accounts import tags


class GoogleOAuth2LoginCallbackView(APIView):
    @extend_schema(
        summary="Google OAuth2 Login Callback",
        description="This endpoint is the callback URL for Google OAuth2 login. It handles the response from Google after the user has authenticated.",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def get(self, request):
        redirect_uri = request.build.build_absolute_uri(
            reverse("google_login_callback")
        )
        auth_uri = request.build_absolute_uri()

        user_data = google_callback(redirect_uri, auth_uri)

        try:
            user = User.objects.get(email=user_data["email"])
        except User.DoesNotExist:
            return CustomResponse.error(
                message="No account is associated with this email.",
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
            )

        # Create the jwt token for the frontend to use.
        refresh = RefreshToken.for_user(user)

        return CustomResponse.success(
            message="Login successful.",
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
