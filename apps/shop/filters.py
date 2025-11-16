import django_filters
from .models import Product

# price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
# price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
# category = django_filters.CharFilter(field_name="category__slug", lookup_expr="iexact")

class ProductFilter(django_filters.FilterSet):
    is_featured = django_filters.BooleanFilter(field_name="featured")
    flash_deals = django_filters.BooleanFilter(field_name="flash_deals")

    class Meta:
        model = Product
        fields = {
            'category__name': ['iexact'],
            "price": ["lte", "gte"],
        }
