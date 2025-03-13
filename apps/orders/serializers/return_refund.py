from rest_framework import serializers
from apps.orders.models import Return, Refund


class ReturnRequestSerializer(serializers.ModelSerializer):
    items_to_return = serializers.ListField(
        child=serializers.UUIDField(), required=True
    )  # List of OrderItem IDs to return

    def validate_items_to_return(self, items_to_return):
        """
        Validate that:
        1. The order belongs to the user
        2. The items_to_return belong to the order
        """
        user_profile = self.context["request"].user.profile
        order = self.context["order"]

        # Check if order belongs to user
        if order.customer != user_profile:
            raise serializers.ValidationError(
                "You are not authorized to create a return for this order."
            )
        valid_items = order.items.filter(id__in=items_to_return)
        if len(valid_items) != len(items_to_return):
            raise serializers.ValidationError("Invalid items selected for return.")
        return items_to_return

    def create(self, validated_data):
        """
        Create the Return object and link it to the order.
        """
        order = self.context["order"]
        return_obj = Return.objects.create(
            reason=validated_data["reason"],
            image=validated_data.get("image"),
        )
        order.return_request = return_obj
        order.save()
        return return_obj

    class Meta:
        model = Return
        fields = [
            "reason",
            "image",
            "return_method",
            "items_to_return",
        ]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            "refund_amount",
            "paystack_refund_status",
            "flw_refund_status",
        ]
