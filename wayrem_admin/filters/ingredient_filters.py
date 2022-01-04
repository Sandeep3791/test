import django_filters
from wayrem_admin.models import Ingredients


class IngredientFilter(django_filters.FilterSet):

    class Meta:
        model = Ingredients
        fields = ['ingredients_name', 'ingredients_status']
