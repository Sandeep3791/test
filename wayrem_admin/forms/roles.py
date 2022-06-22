from django import forms
from django.core.validators import validate_image_file_extension
from wayrem_admin.models import Roles, roles_options


class RoleForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Add Role Description...'}))
    choice_status = (("Active", "Active"), ("Inactive", "Inactive"))
    status = forms.ChoiceField(choices=choice_status, widget=forms.Select(attrs={'class': 'form-select', }))

    class Meta:
        model = Roles
        fields = ('role', 'status', 'content')

        error_messages = {
            'role': {
                'unique': "This role already exists.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.required:
                visible.field.widget.attrs['class'] = 'form-control  required-cls'
            else:
                visible.field.widget.attrs['class'] = 'form-control form-select'


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
