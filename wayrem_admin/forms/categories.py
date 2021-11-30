from django import forms
from wayrem_admin.models import Categories, SubCategories


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ("name", "category_image", "tag", "margin")

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'margin': forms.TextInput(attrs={'class': 'form-control'}),
            'category_image': forms.FileInput(attrs={'class': 'form--control-select'}),
            'tag': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }


class CategoryForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control"}))
    margin = forms.CharField(widget=forms.TextInput(
        attrs={'class': "form-control"}))
    tag = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control", 'rows': '3'}), required=False)
    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': "form-control-file"}), required=False)

    def get_category():
        obj = Categories.objects.all()
        choice = [(None, "Select Parent Category")]
        ch = [(r.id, r.name) for r in obj]
        choice.extend(ch)
        print(choice)
        return choice

    choices_role = get_category

    parent_category = forms.ChoiceField(
        choices=choices_role, widget=forms.Select(attrs={'class': 'form-select'}), required=False)

    def clean(self):
        form_data = self.cleaned_data
        if 'name' in form_data:
            name = form_data['name']
            obj = Categories.objects.filter(name=name).first()
            obj_sub = SubCategories.objects.filter(name=name).first()
            try:
                if name.lower() in obj.name.lower() or name in obj_sub.name:
                    # Will raise a error message
                    self._errors["name"] = "Name already exists!"
                    del form_data['name']
            except:
                pass
        return form_data
