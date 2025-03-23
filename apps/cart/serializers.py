from rest_framework import serializers
from apps.common.serializers import SuccessResponseSerializer
from apps.shop.serializers import ProductAddSerializer


class CartItemSerializer(serializers.Serializer):
    product = ProductAddSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, source="__iter__")
    total_items = serializers.IntegerField(source="__len__")
    total_price = serializers.SerializerMethodField()

    class Meta:
        fields = ["items", "total_items", "total_price"]
        
    def get_total_price(self, obj):
        return obj.get_total_price()


class CartAddUpdateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField() 
    quantity = serializers.IntegerField(min_value=1, default=1)
    override = serializers.BooleanField(default=False)

# Responses
class CartResponseSerializer(SuccessResponseSerializer):
    data = CartSerializer()