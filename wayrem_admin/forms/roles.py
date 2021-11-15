from django import forms
from wayrem_admin.models import Roles


class RoleForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Add Role Description...'}))

    class Meta:
        model = Roles
        fields = ('role', 'status', 'content', 'permission')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.required:
                visible.field.widget.attrs['class'] = 'form-control required-cls'
            else:
                visible.field.widget.attrs['class'] = 'form-control'


class RoleViewForm(forms.ModelForm):

    class Meta:
        model = Roles
        fields = ('permission',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.required:
                # visible.field.widget.attrs['class'] = 'form-control required-cls'
                visible.field.widget.attrs['readonly'] = True
            else:
                visible.field.widget.attrs['class'] = 'form-control'
                visible.field.widget.attrs['readonly'] = True
