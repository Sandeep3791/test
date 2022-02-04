import django_filters
from wayrem_admin.models_orders import Orders

class OrderFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='order_date',lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name="order_date", lookup_expr='lte')
    order_ref=django_filters.Filter(field_name='ref_number',lookup_expr='icontains')
    orderrefer=django_filters.Filter(field_name='ref_number',lookup_expr='icontains')
    contact=django_filters.Filter(field_name='order_phone',lookup_expr='icontains')
    customer_name=django_filters.Filter(field_name='customer__first_name',lookup_expr='icontains')
    class Meta:
        model = Orders
        fields = ['order_ref','start_date','end_date','customer','contact','delivery_status','customer_name','orderrefer']


