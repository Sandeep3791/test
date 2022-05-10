import django_filters
from wayrem_admin.models_orders import Orders
from wayrem_admin.models import BusinessType, Customer
from wayrem_admin.utils.constants import *


class OrderFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(
        field_name='order_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(
        field_name="order_date", lookup_expr='lte')
    order_ref = django_filters.Filter(
        field_name='ref_number', lookup_expr='icontains')
    orderrefer = django_filters.Filter(
        field_name='ref_number', lookup_expr='icontains')
    contact = django_filters.Filter(
        field_name='order_phone', lookup_expr='icontains')
    customer_name = django_filters.Filter(
        field_name='customer__first_name', lookup_expr='icontains')
    business_type = django_filters.Filter(
        method='customer_business_type_filter', label="Business type")

    class Meta:
        model = Orders
        fields = ['order_ref', 'start_date', 'end_date', 'customer',
                  'contact', 'status', 'customer_name', 'orderrefer', 'business_type']

    def customer_business_type_filter(self, queryset, name, value):
        business_type_id = int(value)
        if business_type_id == 1:
            return queryset.filter()
        elif business_type_id == 2:
            return queryset.filter(customer__business_type=BUSINESS_TYPE_ID)
        else:
            return queryset.exclude(customer__business_type=BUSINESS_TYPE_ID)
