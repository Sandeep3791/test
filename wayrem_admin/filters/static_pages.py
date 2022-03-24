from django.db.models import Q
import django_filters
from wayrem_admin.models import StaticPages


class StaticPageFilter(django_filters.FilterSet):
    static_page = django_filters.CharFilter(
        method='static_filter', label="Search")

    class Meta:
        model = StaticPages
        fields = ['page_title', 'slug']

    def static_filter(self, queryset, name, value):
        return StaticPages.objects.filter(Q(page_title__icontains=value) | Q(slug__icontains=value))
