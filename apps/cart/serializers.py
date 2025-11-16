from django.core.validators import MinValueValidator
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.common.serializers import SuccessResponseSerializer
from apps.shop.serializers import ProductAddSerializer


class CartItemSerializer(serializers.Serializer):
    product = ProductAddSerializer(read_only=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )


class CartSerializer(serializers.Serializer):
    # explicitly calls your custom __iter__ method, which returns the processed items with Decimal values and product objects
    items = CartItemSerializer(many=True, source="__iter__")
    total_items = serializers.IntegerField(source="__len__")
    total_price = serializers.SerializerMethodField()

    class Meta:
        fields = ["items", "total_items", "total_price"]

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, obj):
        return obj.get_total_price()


class CartAddUpdateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)], default=1)
    override = serializers.BooleanField(default=False)


# Responses
class CartResponseSerializer(SuccessResponseSerializer):
    data = CartSerializer()
