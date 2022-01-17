import django_filters
from wayrem_admin.models import ShippingRates
from django.db.models import Q

class ShippingRatesFilter(django_filters.FilterSet):
    search=django_filters.Filter(method='my_custom_filter',field_name='from_dest',lookup_expr='icontains')
    class Meta:
        model = ShippingRates
        fields = ['search']

    def my_custom_filter(self, queryset, name, value):
        return ShippingRates.objects.filter(
            Q(from_dest__icontains=value) | Q(to_dest__icontains=value) | Q(price__icontains=value) 
        )
