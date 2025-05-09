from rest_framework import serializers

from apps.cart.cart import Cart
from apps.common.serializers import SuccessResponseSerializer
from apps.orders.cart_service import create_order_from_cart, process_cart_for_order

from apps.profiles.models import ShippingAddress
from apps.shop.serializers import ProductSerializer
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import TrackingNumberSerializer
from drf_spectacular.utils import extend_schema_field


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "price", "quantity", "total"]

    def get_total(self, obj):
        return obj.price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_number = TrackingNumberSerializer(read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "payment_status",
            "payment_method",
            "shipping_status",
            "transaction_id",
            "tx_ref",
            "tracking_number",
            "state",
            "city",
            "street_address",
            "shipping_fee",
            "shipping_time",
            "phone_number",
            "postal_code",
            "pending_email_sent",
            "processing_at",
            "in_transit_at",
            "delivered_at",
            "cancelled_at",
            "created",
            "items",
            "total_cost",
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_cost(self, obj):
        return obj.get_total_cost()


class OrderCreateSerializer(
    serializers.ModelSerializer
):  # Cart(request) will get it for the authenticated user
    shipping_id = serializers.UUIDField()

    class Meta:
        model = Order
        fields = ["shipping_id"]

    def validate_shipping_id(self, shipping_id):
        """
        Validate the shipping ID by ensuring the shipping address exists and belongs to the user.
        """
        # Ensure the shipping address exists and belongs to the user
        try:
            user_profile = self.context["request"].user.profile
            ShippingAddress.objects.get(id=shipping_id, user=user_profile)

        except ShippingAddress.DoesNotExist:
            raise serializers.ValidationError(
                "Shipping address not found or does not belong to the user."
            )

        return shipping_id

    def validate(self, data):
        """
        Perform additional validation, including checking if the cart is empty and stock availability.
        """

        # Initialize the cart instance
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is missing.")

        # Use the cart service
        try:
            process_cart_for_order(request)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return data

    def create(self, validated_data):
        """
        Create the order and its associated items.
        """
        shipping_id = validated_data.get("shipping_id")
        user_profile = self.context["request"].user.profile

        # Initialize the cart instance
        request = self.context.get("request")
        cart = Cart(request)

        # Retrieve the shipping address
        shipping_address = ShippingAddress.objects.get(
            id=shipping_id, user=user_profile
        )

        order = create_order_from_cart(cart, shipping_address, user_profile)

        return order

# RESPONSES
class OrderResponseSerializer(SuccessResponseSerializer):
    data = OrderSerializer()