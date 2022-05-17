from django.db.models import Q
import django_filters
from wayrem_admin.models.BankModels import Banks


class BankFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='bank_filter', label="Search")

    class Meta:
        model = Banks
        fields = ['q']

    def bank_filter(self, queryset, name, value):
        return Banks.objects.filter( Q(is_deleted=0) & Q(title__icontains=value) | Q(bank_name__icontains=value) | Q(account_name__icontains=value))
