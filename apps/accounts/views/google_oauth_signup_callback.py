from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status

from drf_spectacular.utils import extend_schema

from apps.accounts.emails import SendEmail
from apps.accounts.models import User


from apps.accounts.tasks import download_and_upload_avatar
from apps.accounts.utils import google_callback
from apps.common.errors import ErrorCode
from apps.common.responses import CustomResponse

import logging

logger = logging.getLogger(__name__)


@extend_schema(exclude=True)
class GoogleOAuth2SignUpCallbackView(APIView):

    def get(self, request):
        redirect_uri = request.build_absolute_uri(reverse("google_signup_callback"))
        auth_uri = request.build_absolute_uri()
        state = request.query_params.get("state")

        if not state:
            return CustomResponse.error(
                message="State parameter is missing.",
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
            )

        logger.debug(f"Redirect uri: {redirect_uri}")
        logger.debug(f"Auth uri: {auth_uri}")
        logger.debug(f"State: {state}")

        user_data = google_callback(redirect_uri, auth_uri, state)

        # Use get_or_create since an existing user may end up signing in
        # through the sign up route.
        user, created = User.objects.get_or_create(
            email=user_data["email"],
            defaults={
                "first_name": user_data["given_name"],
                "last_name": user_data["family_name"],
                "google_id": user_data["id"],
                "is_email_verified": True,
            },
        )

        avatar_url = user_data.get("picture")
        download_and_upload_avatar.delay(avatar_url, user.id)

        # Create the jwt token for the frontend to use.
        refresh = RefreshToken.for_user(user)

        # send a welcome email
        if created:
            SendEmail.welcome(request, user)

        # if new or existing user, log in the user
        if not created:
            return CustomResponse.success(
                message="Login successful.",
                data={
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status_code=status.HTTP_200_OK,
            )

        return CustomResponse.success(
            message="User created successfully.",
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status_code=status.HTTP_201_CREATED,
        )
