from django.db.models import Q
import django_filters
from wayrem_admin.models import PurchaseOrder


class POFilter(django_filters.FilterSet):
    po = django_filters.CharFilter(
        method='po_filter', label="Search")

    class Meta:
        model = PurchaseOrder
        fields = ['po']

    def po_filter(self, queryset, name, value):
        return PurchaseOrder.objects.filter(
            Q(po_name__icontains=value) | Q(
                status__icontains=value) | Q(supplier_name__company_name__icontains=value)
        )
