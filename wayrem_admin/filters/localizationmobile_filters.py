from django.db.models import Q
import django_filters
from wayrem_admin.models import LocalizationMobileSettings


class LocalizationMobileFilter(django_filters.FilterSet):
    settings = django_filters.CharFilter(
        method='settings_filter', label="Search")

    class Meta:
        model = LocalizationMobileSettings
        fields = ['localization_key']

    def settings_filter(self, queryset, name, value):
        return LocalizationMobileSettings.objects.filter(Q(localization_key__icontains=value) )
