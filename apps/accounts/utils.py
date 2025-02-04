from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.models import Otp


def validate_password_strength(value):
    try:
        validate_password(value)  # This invokes all default password validators
    except DjangoValidationError as e:
        raise serializers.ValidationError(e.messages)  # Raise any validation errors
    return value


def invalidate_previous_otps(user):
    Otp.objects.filter(user=user).delete()


"""
[{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]"""
