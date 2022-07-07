from django import forms
from django.template.defaultfilters import default
from wayrem_admin.models import Categories


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ("name", "image", "tag", "margin")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 35}),
            'margin': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form--control-select'}),
            'tag': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }


UNIT = (
    ('absolute ', 'abs'),
    ('%', '%'),
)


def get_category():
    obj = Categories.objects.filter(is_parent=False)
    choice = [(None, "Select Parent Category"), (None, "None")]
    ch = [(r.name, r.name) for r in obj]
    choice.extend(ch)
    print(choice)
    return choice


choices_role = get_category


class CategoryForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control", 'maxlength': 35}))
    margin = forms.CharField(widget=forms.NumberInput(
        attrs={'class': "form-control"}), initial=0)
    unit = forms.CharField(widget=forms.Select(choices=UNIT, attrs={
                           'class': 'form-select'}), required=True)
    tag = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}), required=False)
    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-file-input"}), required=False)

    parent_category = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)

    def clean(self):
        form_data = self.cleaned_data
        if 'name' in form_data:
            name = form_data['name']
            obj = Categories.objects.filter(name=name).first()
            try:
                if name in obj.name:
                    # Will raise a error message
                    self._errors["name"] = "Name already exists!"
                    del form_data['name']
            except:
                pass
        return form_data


class CategoryUpdateForm(forms.ModelForm):

    parent_category = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)

    class Meta:
        model = Categories
        fields = ("name", "image", "tag", "margin", "unit", "categories_order")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'margin': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input'}),
            'categories_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'tag': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }


class CategorySearchFilter(forms.Form):
    category = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
