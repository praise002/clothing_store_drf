from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status

from drf_spectacular.utils import extend_schema

from apps.accounts.emails import SendEmail
from apps.accounts.models import User

from apps.accounts.utils import google_callback
from apps.common.responses import CustomResponse
from apps.common.serializers import SuccessResponseSerializer
from .accounts import tags

class GoogleOAuth2SignUpCallbackView(APIView):
    @extend_schema(
        summary="Google OAuth2 Sign Up Callback",
        description="This endpoint is the callback URL for Google OAuth2 sign up. It handles the response from Google after the user has authenticated.",
        responses={
            200: SuccessResponseSerializer,
            201: SuccessResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def get(self, request):
        redirect_uri = request.build_absolute_uri(reverse("google_signup_callback"))
        auth_uri = request.build_absolute_uri()

        user_data = google_callback(redirect_uri, auth_uri)

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

        # Create the jwt token for the frontend to use.
        refresh = RefreshToken.for_user(user)
        
        # send a welcome email
        if created:
            SendEmail.welcome(request, user)
        
        # if new or existing user, log in the user
        return CustomResponse.success(
            message="User created successfully.",
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
        
