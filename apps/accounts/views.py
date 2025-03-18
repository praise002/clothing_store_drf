from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError

from drf_spectacular.utils import extend_schema

from apps.accounts.emails import SendEmail
from apps.accounts.utils import invalidate_previous_otps
from apps.common.responses import CustomResponse
from .serializers import (
    LogoutSerializer,
    PasswordChangeSerializer,
    RefreshTokenResponseSerializer,
    RegisterSerializer,
    RequestPasswordResetOtpSerializer,
    SendOtpSerializer,
    SetNewPasswordSerializer,
    VerifyOtpSerializer,
    CustomTokenObtainPairSerializer,
    RegisterResponseSerializer,
    LoginResponseSerializer,
)

from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from .models import User, Otp
from .permissions import IsUnauthenticated

import logging

logger = logging.getLogger(__name__)


tags = ["Auth"]


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Register a new user",
        description="This endpoint registers new users into our application",
        tags=tags,
        responses={
            201: RegisterResponseSerializer,
            400: ErrorDataResponseSerializer,
        },
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializer.validated_data

        # Send OTP for email verification
        SendEmail.send_email(request, user)

        return CustomResponse.success(
            message="OTP sent for email verification.",
            data={"email": data["email"]},
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Login a user",
        description="This endpoint generates new access and refresh tokens for authentication",
        responses={
            200: LoginResponseSerializer,
            404: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get("email"))

            # Check if the user's email is verified
            if not user.is_email_verified:
                # If email is not verified, prompt them to request an OTP

                return CustomResponse.error(
                    message="Email not verified. Please verify your email before logging in.",
                    data={
                        "email": user.email,
                    },
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        except User.DoesNotExist:
            return CustomResponse.error(
                message="User does not exist.", status_code=status.HTTP_404_NOT_FOUND
            )

        # If email is verified, proceed with the normal token generation process
        response = super().post(request, *args, **kwargs)

        # Extract the refresh token from the response
        # refresh_token = response.data.pop("refresh", None)
        # access_token = response.data.get("access")

        # Set the refresh token as an HTTP-only cookie
        # response = CustomResponse.success(
        #     message="Login successful.",
        #     data={
        #         "access_token": access_token,
        #     },
        #     status_code=status.HTTP_200_OK,
        # )
        # response.set_cookie(
        #     key="refresh_token",
        #     value=refresh_token,
        #     httponly=True,  # Prevent JavaScript access
        #     secure=True,    # Only send over HTTPS
        #     samesite="None", # Allow cross-origin requests if frontend and backend are on different domains
        # )

        return response


class ResendVerificationEmailView(APIView):
    serializer_class = SendOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Send OTP to a user's email",
        description="This endpoint sends OTP to a user's email for verification",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CustomResponse.error(
                message="No account is associated with this email.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if user.is_email_verified:
            return CustomResponse.success(
                message="Your email is already verified. No OTP sent.",
                status_code=status.HTTP_200_OK,
            )

        # Invalidate/clear any previous OTPs
        invalidate_previous_otps(user)

        # Send OTP to user's email
        SendEmail.send_email(request, user)

        return CustomResponse.success(
            message="OTP sent successfully.",
            status_code=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    serializer_class = VerifyOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Verify a user's email",
        description="This endpoint verifies a user's email",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            498: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CustomResponse.error(
                message="No account is associated with this email.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check if the OTP is valid for this user
        try:
            otp_record = Otp.objects.get(user=user, otp=otp)
        except Otp.DoesNotExist:
            return CustomResponse.error(
                message="Invalid OTP provided.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check if OTP is expired
        if not otp_record.is_valid:
            return CustomResponse.error(
                message="OTP has expired, please request a new one.",
                status_code=498,
            )

        # Check if user is already verified
        if user.is_email_verified:
            # Clear the OTP
            invalidate_previous_otps(user)
            return CustomResponse.success(
                message="Email address already verified.",
                status_code=status.HTTP_200_OK,
            )

        user.is_email_verified = True
        user.save()

        # Clear OTP after verification
        invalidate_previous_otps(user)

        SendEmail.welcome(request, user)

        return CustomResponse.success(
            message="Email verified successfully.",
            status_code=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(
        summary="Logout a user",
        description="This endpoint logs a user out from our application",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=tags,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return CustomResponse.success(
                message="Logout successful.", status_code=status.HTTP_200_OK
            )

        except TokenError as e:
            return CustomResponse.error(
                message="Invalid or expired refresh token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error during logout: {e}")
            return CustomResponse.error(
                message="An unexpected error occurred. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Clear the HTTP-only cookie containing the refresh token
        # response = CustomResponse.success(
        #     message="Logout successful.", status_code=status.HTTP_200_OK
        # )
        # response.delete_cookie("refresh_token")
        # return response


class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        summary="Change user password",
        description="This endpoint allows authenticated users to update their account password. The user must provide their current password for verification along with the new password they wish to set. If successful, the password will be updated, and a response will confirm the change.",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=tags,
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return CustomResponse.success(
            message="Password changed successfully.", status_code=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    permission_classes = (IsUnauthenticated,)
    serializer_class = RequestPasswordResetOtpSerializer

    @extend_schema(
        summary="Send Password Reset Otp",
        description="This endpoint sends new password reset otp to the user's email",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CustomResponse.error(
                message="User with this email does not exist.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Clear otps if another otp is requested
        invalidate_previous_otps(user)

        # Send OTP to user's email
        SendEmail.send_password_reset_email(request, user)

        return CustomResponse.success(
            message="OTP sent successfully.", status_code=status.HTTP_200_OK
        )


class VerifyOtpView(APIView):
    permission_classes = (IsUnauthenticated,)
    serializer_class = VerifyOtpSerializer

    @extend_schema(
        summary="Verify password reset otp",
        description="This endpoint verifies the password reset OTP.",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            498: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CustomResponse.error(
                message="No account is associated with this email.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check if the OTP is valid for this user
        try:
            otp_record = Otp.objects.get(user=user, otp=otp)
        except Otp.DoesNotExist:
            return CustomResponse.error(
                message="The OTP could not be found. Please enter a valid OTP or request a new one.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check if OTP is expired
        if not otp_record.is_valid:
            return CustomResponse.error(
                message="OTP has expired, please request a new one.", status_code=498
            )

        # Clear OTP after verification
        invalidate_previous_otps(user)

        return CustomResponse.success(
            message="OTP verified, proceed to set new password.",
            status_code=status.HTTP_200_OK,
        )


class PasswordResetDoneView(APIView):
    permission_classes = (IsUnauthenticated,)
    serializer_class = SetNewPasswordSerializer

    @extend_schema(
        summary="Set New Password",
        description="This endpoint sets a new password if the OTP is valid.",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CustomResponse.error(
                message="No account is associated with this email.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Update the user's password
        user.set_password(new_password)
        user.save()

        SendEmail.password_reset_success(request, user)

        return CustomResponse.success(
            message="Your password has been reset, proceed to login.",
            status_code=status.HTTP_200_OK,
        )


class RefreshTokensView(TokenRefreshView):

    @extend_schema(
        summary="Refresh user access token",
        description="This endpoint allows users to refresh their access token using a valid refresh token. It returns a new access token, which can be used for further authenticated requests.",
        tags=tags,
        responses={
            200: RefreshTokenResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to refresh the JWT token
        """
        response = super().post(request, *args, **kwargs)

        # Extract the new refresh token from the response
        # refresh_token = response.data.pop("refresh", None)
        # access_token = response.data.get("access")

        # Set the new refresh token as an HTTP-only cookie
        # response = CustomResponse.success(
        #     message="Token refreshed successfully.",
        #     data={"access_token": access_token},
        #     status_code=status.HTTP_200_OK,
        # )

        # response.set_cookie(
        #     key="refresh_token",
        #     value=refresh_token,
        #     httponly=True,  # Prevent JavaScript access
        #     secure=True,    # Only send over HTTPS
        #     samesite="None", # Allow cross-origin requests if frontend and backend are on different domains
        # )

        response = CustomResponse.success(
            message="Token refreshed successfully.",
            data=response.data,
            status_code=status.HTTP_200_OK,
        )

        return response


# TODO; CREATE CUSTOM RESPONSE FOR SOME OF THE RESPONSES IN EXTEND SCHEMA
# PUT SOME LOGIC IN SERIALIZERS
