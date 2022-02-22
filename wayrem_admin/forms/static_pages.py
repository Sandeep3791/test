from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea, ModelChoiceField
from django import forms
from django.forms import widgets
from wayrem_admin.models import EmailTemplateModel, StaticPages


class StaticpagesForm(forms.ModelForm):
    get_status_dict = {0: 'In Active', 1: 'Active'}
    status_choices = list(get_status_dict.items())
    #status_choices.insert(0,('','Select Status'))
    status = forms.ChoiceField(choices=status_choices, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = StaticPages
        fields = ("page_title", "slug", "description", 'status')
        widgets = {
            'page_title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'cols': 3, 'rows': 3}),
        }


class StaticpagesViewForm(forms.ModelForm):
    get_status_dict = {0: 'InActive', 1: 'Active'}
    status_choices = list(get_status_dict.items())
    #status_choices.insert(0,('','Select Status'))
    status = forms.ChoiceField(
        choices=status_choices, widget=forms.Select(attrs={'class': 'form-select'}))
    description = forms.CharField(widget=CKEditorWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['page_title'].widget.attrs['readonly'] = True
        self.fields['slug'].widget.attrs['readonly'] = True
        self.fields['description'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True

    class Meta:
        model = StaticPages
        fields = ("page_title", "slug", "description", 'status')
        readonly_fields = ["page_title"]
        widgets = {
            'page_title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'cols': 3, 'rows': 3}),
        }
