import django_filters
from apps.orders.choices import ShippingStatus
from apps.orders.models import Order


class OrderFilter(django_filters.FilterSet):
    shipping_status = django_filters.ChoiceFilter(choices=ShippingStatus.choices)
    
    class Meta:
        model = Order
        fields = ["shipping_status"]
