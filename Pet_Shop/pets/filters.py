import django_filters

from .models import Items


class ItemsFilter(django_filters.FilterSet):
    category_id = django_filters.NumberFilter(field_name="category_id")
    price = django_filters.RangeFilter(field_name="price")

    class Meta:
        model = Items
        fields = ["category_id"]
