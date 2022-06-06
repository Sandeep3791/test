import django_filters
from wayrem_admin.models import Products


class ProductFilter(django_filters.FilterSet):
    date_of_mfg = django_filters.DateTimeFilter(
        field_name='date_of_mfg', lookup_expr='gte')
    date_of_exp = django_filters.DateTimeFilter(
        field_name="date_of_exp", lookup_expr='lte')
    name = django_filters.Filter(
        field_name='name', lookup_expr='icontains')
    SKU = django_filters.Filter(
        field_name='SKU', lookup_expr='icontains')

    class Meta:
        model = Products
        fields = ['name', 'SKU', 'category',
                  'supplier', 'date_of_mfg', 'date_of_exp']
