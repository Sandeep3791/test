from django.db.models import Q
import django_filters
from wayrem_admin.models import Customer
from wayrem_admin.models.StaticModels import CreditSettings


class CustomerFilter(django_filters.FilterSet):
    customer = django_filters.CharFilter(
        method='customer_filter', label="Search")

    class Meta:
        model = Customer
        fields = ['customer']

    def customer_filter(self, queryset, name, value):
        return Customer.objects.filter(
            Q(first_name__icontains=value) | Q(
                last_name__icontains=value) | Q(
                email__icontains=value) | Q(
                business_name__icontains=value) | Q(
                verification_status__icontains=value) | Q(
                registration_number__icontains=value)
        ).order_by("id")


class CreditsFilter(django_filters.FilterSet):
    credit = django_filters.CharFilter(
        method='credit_filter', label="Search")

    class Meta:
        model = CreditSettings
        fields = ['credit']

    def credit_filter(self, queryset, name, value):
        return CreditSettings.objects.filter(
            Q(credit_amount__icontains=value) | Q(
                time_period__icontains=value)
        ).order_by("id")
