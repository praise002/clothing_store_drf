from rest_framework import serializers

from apps.orders.choices import PaymentGateway
from apps.orders.models import Order


class PaymentInitializeSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=PaymentGateway.choices)

    def validate_order_id(self, order_id):
        """
        Ensure the order ID exists.
        """
        # Ensure the order exists and belongs to the user
        try:
            user_profile = self.context["request"].user.profile
            Order.objects.get(id=order_id, customer=user_profile)

        except Order.DoesNotExist:
            raise serializers.ValidationError(
                "Order ID not found or does not belong to the user."
            )

        return order_id
