from django.db.models import Q
import django_filters
from wayrem_admin.models import Settings


class SettingsFilter(django_filters.FilterSet):
    settings = django_filters.CharFilter(
        method='settings_filter', label="Search")

    class Meta:
        model = Settings
        fields = ['key', 'display_name']

    def settings_filter(self, queryset, name, value):
        return Settings.objects.filter(Q(key__icontains=value) | Q(display_name__icontains=value))
