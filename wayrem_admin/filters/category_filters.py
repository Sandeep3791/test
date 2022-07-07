from django.db.models import Q
import django_filters
from wayrem_admin.models import Categories


class CategoriesFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        method='category_filter', label="Search")

    class Meta:
        model = Categories
        fields = ['category']

    def category_filter(self, queryset, name, value):
        return Categories.objects.filter(
            Q(name__icontains=value) | Q(parent__icontains=value) | Q(
                tag__icontains=value)
        ).order_by("categories_order")
