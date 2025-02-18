from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from . import models


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


# def order_detail(obj):
#     url = reverse("orders:admin_order_detail", args=[obj.id])
#     return mark_safe(f'<a href="{url}">View</a>')


# def order_pdf(obj):
#     url = reverse("orders:admin_order_pdf", args=[obj.id])
#     return mark_safe(f'<a href="{url}">PDF</a>')


# order_pdf.short_description = "Invoice"


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = [
        "id",
        "created",
        "customer",
        "payment_ref",
        # order_detail,
        # order_pdf,
    ]


# admin.site.register(models.Delivery)
