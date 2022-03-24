from django import forms
from wayrem_admin.models import Ingredients


class IngredientsCreateForm(forms.ModelForm):
    class Meta:
        model = Ingredients
        fields = ("ingredients_name", "ingredients_status",)

        widgets = {
            'ingredients_name': forms.TextInput(attrs={'class': 'form-control', 'minlength': 3}),
            'ingredients_status': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'ingredients_name': {
                'unique': "This ingredient already exist.",
            },
        }


class IngredientFilterForm(forms.ModelForm):
    ingredients_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)

    class Meta:
        model = Ingredients
        fields = ['ingredients_name']
