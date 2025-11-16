import django_filters
from apps.orders.choices import ShippingStatus
from apps.orders.models import Order


class OrderFilter(django_filters.FilterSet):

    class Meta:
        model = Order
        fields = ["shipping_status"]
