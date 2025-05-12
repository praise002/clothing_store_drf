from rest_framework import serializers

from apps.common.serializers import SuccessResponseSerializer
from apps.discount.models import Coupon


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)
    # order_id comes from URL

    def validate_code(self, code):
        """Check if coupon exists and is valid."""
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_valid:
                raise serializers.ValidationError("Expired coupon code")
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")

        return code


# class CouponSerializer(serializers.ModelSerializer):
#     discount_type = serializers.CharField(source="discount.discount_type")
#     discount_value = serializers.CharField(source="discount.discount_value")
    
#     class Meta:
#         model = Coupon
#         fields = ["code", "discount", "discount_type", "discount_value"]

# class CouponResponseSerializer(SuccessResponseSerializer):
#     data = CategorySerializer()