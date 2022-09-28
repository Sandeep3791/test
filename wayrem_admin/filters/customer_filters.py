from django.db.models import Q
import django_filters
from wayrem_admin.models import Customer, CreditSettings, CreditPaymentReference


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
                contact__icontains=value) | Q(
                email__icontains=value) | Q(
                business_name__icontains=value) | Q(
                verification_status__icontains=value) | Q(
                registration_number__icontains=value), status=True
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


class CreditTxnFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='credit_txn_filter', label="Search")

    class Meta:
        model = CreditPaymentReference
        fields = ['search']

    def credit_txn_filter(self, queryset, name, value):
        return CreditPaymentReference.objects.filter(
            Q(reference_no__icontains=value) | Q(
                customer__first_name__icontains=value) | Q(
                customer__last_name__icontains=value) | Q(payment_status__name__icontains=value) | Q(payment_type__name__icontains=value)).order_by("id")
