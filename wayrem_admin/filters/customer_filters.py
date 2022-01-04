from django.db.models import Q
import django_filters
from wayrem_admin.models import Customer


class CustomerFilter(django_filters.FilterSet):
    customer = django_filters.CharFilter(
        method='customer_filter', label="Search")

    class Meta:
        model = Customer
        fields = ['customer']

    def customer_filter(self, queryset, name, value):
        return Customer.objects.filter(
            Q(first_name__icontains=value) | Q(
                last_name__icontains=value) | Q(country__icontains=value) | Q(
                city__icontains=value) | Q(
                email__icontains=value) | Q(
                business_name__icontains=value) | Q(
                registration_number__icontains=value)
        )
