from django import forms
from wayrem_admin.models import SubCategories


class SubCategoryCreateForm(forms.ModelForm):
    class Meta:
        model = SubCategories
        fields = ("name", "tag", "margin", "category")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'margin': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tag': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }
