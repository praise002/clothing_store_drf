from rest_framework import serializers

from apps.common.errors import ErrorCode


class SuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="success")
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="failure")
    message = serializers.CharField()
    code = serializers.CharField()


class ErrorDataResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="failure")
    message = serializers.CharField()
    code = serializers.CharField()
    data = serializers.DictField(required=False)


class ValidationErrorResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="failure")
    message = serializers.CharField(default="Validation error")
    code = serializers.CharField(default=ErrorCode.VALIDATION_ERROR)
    data = serializers.DictField()


class PaginatedResponseDataSerializer(serializers.Serializer):
    per_page = serializers.IntegerField()
    current_page = serializers.IntegerField()
    last_page = serializers.IntegerField()
