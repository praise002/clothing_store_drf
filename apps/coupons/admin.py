# from django.contrib import admin

# from .models import Coupon, CouponUsage


# @admin.register(Coupon)
# class CouponAdmin(admin.ModelAdmin):
#     list_display = ["code", "valid_from", "valid_to", "discount", "active"]
#     list_filter = ["active", "valid_from", "valid_to"]
#     search_fields = ["code"]
    
# @admin.register(CouponUsage)
# class CouponUsageAdmin(admin.ModelAdmin):
#     list_display = ["profile", "coupon", "redeemed_at"]