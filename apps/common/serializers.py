from rest_framework import serializers


class SuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="success")
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="failure")
    message = serializers.CharField()
    err_code = serializers.CharField()


class ErrorDataResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="failure")
    message = serializers.CharField()
    errors = serializers.DictField(required=False)
    err_code = serializers.CharField()


class PaginatedResponseDataSerializer(serializers.Serializer):
    per_page = serializers.IntegerField()
    current_page = serializers.IntegerField()
    last_page = serializers.IntegerField()
