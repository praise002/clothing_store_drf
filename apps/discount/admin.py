from django.contrib import admin
from . import models

@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass

@admin.register(models.ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass

@admin.register(models.CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    pass