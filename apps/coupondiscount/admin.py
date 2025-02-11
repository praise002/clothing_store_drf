from django.contrib import admin
from . import models


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.DiscountAssignment)
class DiscountAssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrderDiscount)
class OrderDiscountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TieredDiscount)
class TieredDiscountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.FirstPurchaseDiscount)
class FirstPurchaseDiscountAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    pass
