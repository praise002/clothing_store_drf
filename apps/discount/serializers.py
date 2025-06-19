from rest_framework import serializers

from apps.discount.models import Coupon


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)
    # order_id comes from URL

    def validate_code(self, code):
        """Check if coupon exists and is valid."""
        try:
            coupon = Coupon.objects.select_related("discount").get(code=code)
            if not coupon.is_valid:
                raise serializers.ValidationError("Expired coupon code")
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")

        return code
