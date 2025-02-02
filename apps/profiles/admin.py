from django.contrib import admin
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from .models import Profile

from apps.orders.models import Order

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shipping_address', 'orders')
    readonly_fields = ('id', 'last_updated', 'created') 
    raw_id_fields = ('user',)
    list_filter = ('created',) 
    list_per_page = 10
    search_fields = ('first_name__istartswith', 'last_name__istartswith')
    
    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:orders_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('orders')
        )
    
    
admin.site.register(Profile, ProfileAdmin)




    