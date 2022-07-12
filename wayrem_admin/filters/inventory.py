from django.db.models import Q
import django_filters
from wayrem_admin.models import Inventory


class InventoryFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        method='inventory_filter', label="category")
    name = django_filters.CharFilter(
        method='inventory_filter', label="name")
    SKU = django_filters.CharFilter(
        method='inventory_filter', label="SKU")

    class Meta:
        model = Inventory
        fields = ['category', 'name', 'SKU']

    def inventory_filter(self, queryset, name, value):
        return Inventory.objects.filter(
            Q(product__category__name__icontains=value) | Q(
                product__name__icontains=value) | Q(
                product__SKU__icontains=value)).order_by("-id")
