from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


from drf_spectacular.utils import extend_schema

from apps.accounts.emails import SendEmail
from apps.accounts.schema_examples import (
    LOGIN_RESPONSE_EXAMPLE,
    LOGOUT_ALL_RESPONSE_EXAMPLE,
    LOGOUT_RESPONSE_EXAMPLE,
    PASSWORD_CHANGE_RESPONSE_EXAMPLE,
    PASSWORD_RESET_DONE_RESPONSE_EXAMPLE,
    PASSWORD_RESET_REQUEST_RESPONSE_EXAMPLE,
    REFRESH_TOKEN_RESPONSE_EXAMPLE,
    REGISTER_RESPONSE_EXAMPLE,
    RESEND_VERIFICATION_EMAIL_RESPONSE_EXAMPLE,
    VERIFY_EMAIL_RESPONSE_EXAMPLE,
    VERIFY_OTP_RESPONSE_EXAMPLE,
)
from apps.accounts.utils import invalidate_previous_otps
from apps.common.errors import ErrorCode
from apps.common.responses import CustomResponse
from apps.accounts.serializers import (
    PasswordChangeSerializer,
    RegisterSerializer,
    RequestPasswordResetOtpSerializer,
    SendOtpSerializer,
    SetNewPasswordSerializer,
    VerifyOtpSerializer,
    CustomTokenObtainPairSerializer,
)


from apps.accounts.models import User, Otp
from apps.accounts.permissions import IsUnauthenticated

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
        responses=REGISTER_RESPONSE_EXAMPLE,
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
        responses=LOGIN_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            user = User.objects.get(email=request.data.get("email"))
            # Check if the user's email is verified
            if not user.is_email_verified:
                # If email is not verified, prompt them to request an OTP

                return CustomResponse.error(
                    message="Email not verified. Please verify your email before logging in.",
                    status_code=status.HTTP_403_FORBIDDEN,
                    err_code=ErrorCode.FORBIDDEN,
                )
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Extract the refresh token from the response
        # refresh = response.data.pop("refresh", None)
        # access = response.data.get("access")

        # Set the refresh token as an HTTP-only cookie
        # response = CustomResponse.success(
        #     message="Login successful.",
        #     data={
        #         "access": access_token,
        #     },
        #     status_code=status.HTTP_200_OK,
        # )
        # response.set_cookie(
        #     key="refresh",
        #     value=refresh,
        #     httponly=True,  # Prevent JavaScript access
        #     secure=True,    # Only send over HTTPS
        #     samesite="None", # Allow cross-origin requests if frontend and backend are on different domains
        # )

        response = CustomResponse.success(
            message="Login successful.",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
        )

        return response


class ResendVerificationEmailView(APIView):
    serializer_class = SendOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Send OTP to a user's email",
        description="This endpoint sends OTP to a user's email for verification",
        responses=RESEND_VERIFICATION_EMAIL_RESPONSE_EXAMPLE,
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
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
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
        responses=VERIFY_EMAIL_RESPONSE_EXAMPLE,
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
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
            )

        # Check if the OTP is valid for this user
        try:
            otp_record = Otp.objects.get(user=user, otp=otp)
        except Otp.DoesNotExist:
            return CustomResponse.error(
                message="Invalid OTP provided.",
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
            )

        # Check if OTP is expired
        if not otp_record.is_valid:
            return CustomResponse.error(
                message="OTP has expired, please request a new one.",
                status_code=498,
                err_code=ErrorCode.EXPIRED,
            )

        # Check if user is already verified
        if user.is_email_verified:
            # Clear the OTP
            invalidate_previous_otps(user)
            return CustomResponse.success(
                message="Email address already verified. No OTP sent.",
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


class LogoutView(TokenBlacklistView):
    @extend_schema(
        summary="Logout a user",
        description="This endpoint logs a user out from our application",
        responses=LOGOUT_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = CustomResponse.success(
            message="Logged out successfully.", status_code=status.HTTP_200_OK
        )
        return response

        # Clear the HTTP-only cookie containing the refresh token
        # response.delete_cookie("refresh")
        # return response


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout from all devices",
        description="Blacklists all refresh tokens for the user",
        tags=tags,
        responses=LOGOUT_ALL_RESPONSE_EXAMPLE,
    )
    def post(self, request):
        try:
            # Get all valid tokens for the user
            tokens = OutstandingToken.objects.filter(
                user=request.user, expires_at__gt=timezone.now(), blacklistedtoken=None
            )

            # Blacklist all tokens
            for token in tokens:
                RefreshToken(token.token).blacklist()

            return CustomResponse.success(
                message="Successfully logged out from all devices.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return CustomResponse.error(
                message="Error during logout",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                err_code=ErrorCode.SERVER_ERROR,
            )


class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        summary="Change user password",
        description="This endpoint allows authenticated users to update their account password. The user must provide their current password for verification along with the new password they wish to set. If successful, the password will be updated, and a response will confirm the change.",
        responses=PASSWORD_CHANGE_RESPONSE_EXAMPLE,
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
        responses=PASSWORD_RESET_REQUEST_RESPONSE_EXAMPLE,
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
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
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
        responses=VERIFY_OTP_RESPONSE_EXAMPLE,
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
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
            )

        # Check if the OTP is valid for this user
        try:
            otp_record = Otp.objects.get(user=user, otp=otp)
        except Otp.DoesNotExist:
            return CustomResponse.error(
                message="The OTP could not be found. Please enter a valid OTP or request a new one.",
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
            )

        # Check if OTP is expired
        if not otp_record.is_valid:
            return CustomResponse.error(
                message="OTP has expired, please request a new one.",
                status_code=498,
                err_code=ErrorCode.EXPIRED,
            )

        # Clear OTP after verification
        invalidate_previous_otps(user)

        return CustomResponse.success(
            message="OTP verified, proceed to set a new password.",
            status_code=status.HTTP_200_OK,
        )


class PasswordResetDoneView(APIView):
    permission_classes = (IsUnauthenticated,)
    serializer_class = SetNewPasswordSerializer

    @extend_schema(
        summary="Set New Password",
        description="This endpoint sets a new password if the OTP is valid.",
        responses=PASSWORD_RESET_DONE_RESPONSE_EXAMPLE,
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
                status_code=status.HTTP_400_BAD_REQUEST,
                err_code=ErrorCode.BAD_REQUEST,
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
        responses=REFRESH_TOKEN_RESPONSE_EXAMPLE,
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to refresh the JWT token
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Extract the new refresh token from the response
        # refresh = response.data.pop("refresh", None)
        # access = response.data.get("access")

        # Set the new refresh token as an HTTP-only cookie
        # response = CustomResponse.success(
        #     message="Token refreshed successfully.",
        #     data={"access": access},
        #     status_code=status.HTTP_200_OK,
        # )

        # response.set_cookie(
        #     key="refresh",
        #     value=refresh,
        #     httponly=True,  # Prevent JavaScript access
        #     secure=True,    # Only send over HTTPS
        #     samesite="None", # Allow cross-origin requests if frontend and backend are on different domains
        # )

        response = CustomResponse.success(
            message="Token refreshed successfully.",
            data=serializer.validated_data,
            status_code=status.HTTP_200_OK,
        )

        return response


# TODO: TEST THE COOKIE STUFF

# import os
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Add this at the top of the file

# from decouple import config
# client_id = config('GOOGLE_CLIENT_ID')
# client_secret = config('GOOGLE_CLIENT_SECRET')
# redirect_uri = 'http://127.0.0.1:8000/google/callback/signup'

# authorization_base_url = config('GOOGLE_AUTH_URL')
# token_url = config('GOOGLE_TOKEN_URL')
# scope = [
#     "openid",
#     "https://www.googleapis.com/auth/userinfo.email",
#     "https://www.googleapis.com/auth/userinfo.profile"
# ]

# from requests_oauthlib import OAuth2Session
# google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

# # Redirect user to Google for authorization
# authorization_url, state = google.authorization_url(authorization_base_url,
#     # offline for refresh token
#     # force to always make user click authorize
#     access_type="offline", prompt="select_account")
# print('Please go here and authorize:', authorization_url)

# # Get the authorization verifier code from the callback url
# redirect_response = input('Paste the full redirect URL here: ')

# # Fetch the access token
# google.fetch_token(token_url, client_secret=client_secret,
#         authorization_response=redirect_response)

# # Fetch a protected resource, i.e. user profile
# r = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
# print(r.content)

# http://127.0.0.1:8000/google/callback/signup?state=1aK0aAakbIOh1fd3IZxnQ4jkB5x3k7&code=4%2F0Ab_5qlk5JZGVEAI_Rya_Wx2wrVOkZ27CpYUhV-4UdIKOFhd1lINHCFgyPtLhP3KhpxV5rA&scope=email+profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&authuser=0&prompt=consent
# https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=725113392766-5fd01j0lkh67v5qfolli2ihtrlgbdlhj.apps.googleusercontent.com&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fgoogle%2Fcallback%2Fsignup&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile&state=1aK0aAakbIOh1fd3IZxnQ4jkB5x3k7&access_type=offline&prompt=select_account
# b'{\n  "id": "104652954164547380135",\n  "email": "ifeoluwapraise02@gmail.com",\n  "verified_email": true,\n  "name": "Praise Idowu",\n  "given_name": "Praise",\n  "family_name": "Idowu",\n  "picture": "https://lh3.googleusercontent.com/a/ACg8ocJl-uFIznNDVQ7Q3nKp40-hkTvwWUTZ4LbEqDr2rzHTYtm6N4sj=s96-c"\n}\n'
#  python manage.py runserver_plus --cert-file cert.crt
