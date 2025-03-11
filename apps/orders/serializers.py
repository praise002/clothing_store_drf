from rest_framework import serializers

from decimal import Decimal

from apps.cart.cart import Cart
from apps.profiles.models import ShippingAddress
from apps.shop.serializers import ProductSerializer
from .models import Order, OrderItem, Refund, Return, TrackingNumber


class TrackingNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingNumber
        fields = ["number"]


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

        cart = Cart(request)

        # Ensure the cart is not empty
        if not cart.cart or not any(
            cart.cart.values()
        ):  #  falsy evaluates to true if cart is empty
            raise serializers.ValidationError("The cart is empty.")

        # Check stock availability for each item in the cart
        for item in cart:
            product = item["product"]
            quantity = item["quantity"]

            # Check if enough stock available
            if product.in_stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.in_stock}"
                )

        return data

    def create(self, validated_data):
        """
        Create the order and its associated items.
        """
        shipping_id = validated_data.get("shipping_id")

        # Initialize the cart instance
        request = self.context.get("request")
        cart = Cart(request)

        # Retrieve the shipping address
        shipping_address = ShippingAddress.objects.get(
            id=shipping_id, user=request.user.profile
        )
        # Save the state and shipping fee in case the address is deleted or updated
        state = shipping_address.state
        city = shipping_address.city
        street_address = shipping_address.street_address
        shipping_fee = shipping_address.shipping_fee
        phone_number = shipping_address.phone_number
        postal_code = shipping_address.postal_code

        # Create the order
        order = Order.objects.create(
            customer=request.user.profile,
            state=state,
            city=city,
            street_address=street_address,
            shipping_fee=shipping_fee,
            phone_number=phone_number,
            postal_code=postal_code,
        )

        # Add items from the cart to the order
        for item in cart:
            product = item["product"]
            quantity = item["quantity"]
            price = Decimal(item["price"])

            # Create order item and reduce stock
            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=price
            )
            product.in_stock -= quantity
            product.save()

        # Clear the cart after creating the order
        cart.clear()

        return order


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
            tracking_number=validated_data.get("tracking_number"),
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
            "tracking_number",
            "items_to_return",
        ]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            "partial_refund",
            "refund_amount",
            "paystack_refund_status",
            "flw_refund_status",
        ]
