from django.shortcuts import redirect
from django.urls import reverse

from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from apps.accounts.utils import google_setup
from .accounts import tags

class GoogleOAuth2LoginView(APIView):
    @extend_schema(
        summary="Google OAuth2 Login",
        description="This endpoint is the login URL for Google OAuth2. It redirects the user to the Google authentication page.",
        tags=tags,
        auth=[],
    )
    def get(self, request):
        # The redirect_uri should match the settings shown on the GCP OAuth config page.
        # The call to build_absolute_uri returns the full URL including domain.
        redirect_uri = request.build_absolute_uri(reverse("google_login_callback"))
        return redirect(google_setup(redirect_uri))
