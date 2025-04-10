from rest_framework import serializers


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


class PaginatedResponseDataSerializer(serializers.Serializer):
    per_page = serializers.IntegerField()
    current_page = serializers.IntegerField()
    last_page = serializers.IntegerField()
