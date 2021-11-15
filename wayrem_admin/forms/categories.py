from django import forms
from wayrem_admin.models import Categories


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ("name", "category_image", "description")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'category_image': forms.ImageField(attrs={'class': 'form-control-file'}),
            # 'category_image': forms.FieldInput(widget=forms.FileInput(attrs={'class': 'rounded_list'})),
            'category_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }
