from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from django.core.validators import MinValueValidator, MaxValueValidator

from apps.accounts.utils import validate_password_strength
from apps.common.schema_examples import ACCESS_TOKEN, REFRESH_TOKEN
from apps.common.serializers import SuccessResponseSerializer
from .models import User


# REQUEST SERIALIZERS
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Use the custom user manager to create a user with the validated data
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        return user

    def validate_password(self, value):
        return validate_password_strength(value)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get the standard token with default claims
        token = super().get_token(user)
        # Add custom claim for full name
        token["full_name"] = user.full_name
        return token


class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOtpSerializer(serializers.Serializer):
    email = (
        serializers.EmailField()
    )  # the frontend keeps the email in state then supplies it here
    otp = serializers.IntegerField(
        validators=[MinValueValidator(100000), MaxValueValidator(999999)]
    )


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"error": "New password and confirm password do not match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {
                    "error": "The current password you entered is incorrect. Please try again."
                }
            )

        return value

    def validate_new_password(self, value):
        return validate_password_strength(value)

    def save(self, **kwargs):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        # Blacklist all active refresh tokens for the user
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)


class RequestPasswordResetOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"error": "New password and confirm password do not match."}
            )
        return attrs

    def validate_new_password(self, value):
        return validate_password_strength(value)


# RESPONSES
class RegisterResponseSerializer(SuccessResponseSerializer):
    email = serializers.EmailField(default="bob123@example.com")


class LoginResponseSerializer(SuccessResponseSerializer):
    data = serializers.DictField(
        default={
            "refresh": REFRESH_TOKEN,
            "access": ACCESS_TOKEN,
        }
    )

class RefreshTokenResponseSerializer(SuccessResponseSerializer):
    data = serializers.DictField(
        default={
            "access": ACCESS_TOKEN,
            "refresh": REFRESH_TOKEN,
        }
    )