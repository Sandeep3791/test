from django.db.models import Q
import django_filters
from wayrem_admin.models import Invoice


class SupplierInvoiceFilter(django_filters.FilterSet):
    supplier_invoice = django_filters.CharFilter(
        method='supplier_invoice_filter', label="Search")

    class Meta:
        model = Invoice
        fields = ['po_name', 'supplier_name']

    def supplier_invoice_filter(self, queryset, name, value):
        return Invoice.objects.filter(Q(po_name__icontains=value) | Q(supplier_name__icontains=value))
