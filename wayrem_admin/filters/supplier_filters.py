from django.db.models import Q
import django_filters
from wayrem_admin.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    supplier = django_filters.CharFilter(
        method='supplier_filter', label="Search")

    class Meta:
        model = Supplier
        fields = ['username', 'email']

    def supplier_filter(self, queryset, name, value):
        return Supplier.objects.filter(Q(username__icontains=value) | Q(email__icontains=value))
