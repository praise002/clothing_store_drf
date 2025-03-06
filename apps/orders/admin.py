from django.contrib import admin
from . import models


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = [
        "id",
        "created",
        "customer",
        "transaction_id",
    ]

admin.site.register(models.TrackingNumber)