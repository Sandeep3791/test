from django.db.models import Q
import django_filters
from wayrem_admin.models import User


class UserFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(
        method='user_filter', label="Search")

    class Meta:
        model = User
        fields = ['category']

    def user_filter(self, queryset, name, value):
        return User.objects.filter(
            Q(username__icontains=value) | Q(
                email__icontains=value) | Q(contact__icontains=value)
        )
