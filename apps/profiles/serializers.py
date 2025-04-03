from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.common.serializers import SuccessResponseSerializer


from .models import Profile, ShippingAddress


User = get_user_model()


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "id",
            "user",
            "phone_number",
            "state",
            "postal_code",
            "city",
            "street_address",
            "shipping_fee",
            "shipping_time",
            "default",
        ]
        read_only_fields = [
            "user",
            "shipping_fee",
            "shipping_time",
        ]


class ShippingAddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "phone_number",
            "state",
            "postal_code",
            "city",
            "street_address",
            "default",  # Allow setting as default during creation
        ]

    def create(self, validated_data):
        # Get the authenticated user's profile
        user = self.context["request"].user.profile
        default = validated_data.pop(
            "default", False
        )  # ensures that the behavior is consistent and predictable, even if the "default" key is not explicitly provided in the request

        # If marking as default, unmark all other addresses for the user
        if default:
            ShippingAddress.objects.filter(user=user).update(default=False)

        # Create the shipping address and associate it with the user
        shipping_address = ShippingAddress.objects.create(
            user=user, default=default, **validated_data
        )
        return shipping_address


class ShippingAddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            "phone_number",
            "state",
            "postal_code",
            "city",
            "street_address",
            "default",  # Allow updating the default status
        ]

    def update(self, instance, validated_data):
        default = validated_data.pop("default", None)

        # If marking as default, unmark all other addresses for the user
        if default and default is True:
            ShippingAddress.objects.filter(user=instance.user).update(default=False)
            instance.default = True

        # Update the shipping address
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
        }


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "last_updated",
            "avatar_url",
        ]

    @extend_schema_field(serializers.URLField)
    def get_avatar_url(self, obj):
        return obj.avatar_url


class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "avatar",
        ]


# RESPONSES
class ShippingAddressResponseSerializer(SuccessResponseSerializer):
    data = ShippingAddressSerializer()


class ProfileResponseSerializer(SuccessResponseSerializer):
    data = ProfileSerializer()
