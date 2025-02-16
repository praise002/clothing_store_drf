from rest_framework import serializers

from apps.common.validators import validate_uuid
from apps.shop.serializers import ProductSerializer
from .models import Order, OrderItem


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
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "order_status",
            "payment_status",
            "shipping_status",
            "payment_ref",
            "tracking_number",
            "state",
            "shipping_fee",
            "created",
            "items",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id = serializers.UUIDField()
    shipping_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not validate_uuid(cart_id):
            raise serializers.ValidationError("Invalid cart ID format.")
        return cart_id

    def validate_shipping_id(self, shipping_id):
        if not validate_uuid(shipping_id):
            raise serializers.ValidationError("Invalid shipping ID format.")
        return shipping_id
