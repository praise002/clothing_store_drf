from django.contrib.auth import get_user_model
from rest_framework import serializers


from .models import Profile


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "shipping_address",
            "postal_code",
            "city",
            "phone",
            "last_updated",
            "avatar_url",
        ]
