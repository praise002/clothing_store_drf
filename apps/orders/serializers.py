from rest_framework import serializers

from decimal import Decimal

from apps.cart.cart import Cart
from apps.common.validators import validate_uuid
from apps.profiles.models import ShippingAddress
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
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "payment_status",
            "payment_method",
            "shipping_status",
            "reference",
            "transaction_id",
            "tracking_number",
            "state",
            "shipping_fee",
            "date_delivered",
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
        fields = ['shipping_id']

    def validate_cart_id(self, cart_id):
        """
        Ensure the cart is not empty.
        """

        # Initialize the cart instance
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is missing.")

        cart = Cart(request)
        if not cart.cart or not any(
            cart.cart.values()
        ):  #  falsy evaluates to true if cart is empty
            raise serializers.ValidationError("The cart is empty.")

        return cart_id

    def validate_shipping_id(self, shipping_id):
        """
        Validate the shipping ID format and ensure the shipping address exists.
        """
        if not validate_uuid(shipping_id):
            raise serializers.ValidationError("Invalid shipping ID format.")

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
        Perform additional validation (e.g., stock availability).
        """

        # Initialize the cart instance
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is missing.")

        cart = Cart(request)

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
            shipping_address=shipping_address,
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
