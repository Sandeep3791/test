from django.db.models import Q
import django_filters
from wayrem_admin.models import Inventory
from wayrem_admin.models.orders import Orders


class InventoryFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        method='inventory_filter', label="category")
    name = django_filters.CharFilter(
        method='inventory_filter', label="name")
    mfr_name = django_filters.CharFilter(
        method='inventory_filter', label="mfr_name")
    customer = django_filters.CharFilter(
        method='inventory_customer_filter', label="customer")
    SKU = django_filters.CharFilter(
        method='inventory_filter', label="SKU")

    class Meta:
        model = Inventory
        fields = ['category', 'name', 'SKU', 'mfr_name', 'customer']

    def inventory_filter(self, queryset, name, value):
        return Inventory.objects.filter(
            Q(product__category__name__icontains=value) | Q(
                product__name__icontains=value) | Q(
                product__SKU__icontains=value) | Q(
                product__mfr_name__icontains=value)).order_by("-id")

    def inventory_customer_filter(self, queryset, name, value):
        order_id = Orders.objects.filter(
            Q(customer__first_name__icontains=value) | Q(
                customer__last_name__icontains=value) | Q(
                customer__email__icontains=value) | Q(
                customer__contact__icontains=value))
        return Inventory.objects.filter(Q(order_id__in=order_id))
