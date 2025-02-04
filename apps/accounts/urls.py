from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    path("token/", views.LoginView.as_view()),
    path("token/refresh/", views.RefreshTokensView.as_view()),
    path("token/revoke/", views.LogoutView.as_view()),
    path("otp/", views.ResendVerificationEmailView.as_view()),
    path("otp/verify/", views.VerifyEmailView.as_view()),
    path("password-change/", views.PasswordChangeView.as_view()),
    path("password-reset/otp/", views.PasswordResetRequestView.as_view()),
    path("password-reset/otp/verify/", views.VerifyOtpView.as_view()),
    path("password-reset/done/", views.PasswordResetDoneView.as_view()),
]
