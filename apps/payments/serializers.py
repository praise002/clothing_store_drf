from rest_framework import serializers

from apps.common.validators import validate_uuid
from apps.orders.choices import PaymentGateway
from apps.orders.models import Order


class PaymentInitializeSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=PaymentGateway.choices)
    
    def validate_order_id(self, order_id):
        """
        Validate the order ID format and ensure the order ID exists.
        """
        if not validate_uuid(order_id):
            raise serializers.ValidationError("Invalid order ID format.")

        # Ensure the order exists and belongs to the user
        try:
            user_profile = self.context["request"].user.profile
            Order.objects.get(id=order_id, customer=user_profile)

        except Order.DoesNotExist:
            raise serializers.ValidationError(
                "Order ID not found or does not belong to the user."
            )

        return order_id
