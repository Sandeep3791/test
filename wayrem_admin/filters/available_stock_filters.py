import django_filters
from wayrem_admin.utils.constants import *
from wayrem_admin.models import Products

class AvailableStockFilter(django_filters.FilterSet):
    search = django_filters.Filter(
        method='customer_business_type_filter', label="Search")

    class Meta:
        model = Products
        fields = ['search']

    def customer_business_type_filter(self, queryset, name, value):
        search = (value)
        return queryset.filter(SKU__contains=search)