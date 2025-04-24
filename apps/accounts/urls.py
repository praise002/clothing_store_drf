from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    path("token/", views.LoginView.as_view()),
    path("token/refresh/", views.RefreshTokensView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path("logout/", views.LogoutView.as_view()),
    path("logout/all/", views.LogoutAllView.as_view()),
    path("otp/", views.ResendVerificationEmailView.as_view()),
    path("otp/verify/", views.VerifyEmailView.as_view()),
    path("password-change/", views.PasswordChangeView.as_view()),
    path("password-reset/otp/", views.PasswordResetRequestView.as_view()),
    path("password-reset/otp/verify/", views.VerifyOtpView.as_view()),
    path("password-reset/done/", views.PasswordResetDoneView.as_view()),
    # Oauth
    path(
        "signup/google/", views.GoogleOAuth2SignUpView.as_view(), name="google_signup"
    ),
    path(
        "google/callback/signup",
        views.GoogleOAuth2SignUpCallbackView.as_view(),
        name="google_signup_callback",
    ),
    path("login/google/", views.GoogleOAuth2LoginView.as_view(), name="google_login"),
    path(
        "google/callback/login",
        views.GoogleOAuth2LoginCallbackView.as_view(),
        name="google_login_callback",
    ),
]
