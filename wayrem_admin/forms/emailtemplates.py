from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea, ModelChoiceField
from django import forms
from django.forms import widgets
from wayrem_admin.models import EmailTemplateModel


class EmailtemplatesForm(forms.ModelForm):
    get_status_dict = {0: 'In Active', 1: 'Active'}
    status_choices = list(get_status_dict.items())
    #status_choices.insert(0,('','Select Status'))
    status = forms.ChoiceField(choices=status_choices, widget=forms.Select(
        attrs={'class': 'form-control form-control-select'}))
    message_format = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = EmailTemplateModel
        fields = ("name", "key", "from_email", "to_email",
                  "subject", "message_format", 'status')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'from_email': forms.TextInput(attrs={'class': 'form-control'}),
            'to_email': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message_format': Textarea(attrs={'cols': 3, 'rows': 3}),
        }


class EmailtemplatesViewForm(forms.ModelForm):
    get_status_dict = {0: 'In Active', 1: 'Active'}
    status_choices = list(get_status_dict.items())
    #status_choices.insert(0,('','Select Status'))
    status = forms.ChoiceField(
        choices=status_choices, widget=forms.Select(attrs={'class': 'form-control form-control-select','disabled':'disabled'}))
    message_format = forms.CharField(widget=CKEditorWidget())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['key'].widget.attrs['readonly'] = True
        self.fields['from_email'].widget.attrs['readonly'] = True
        self.fields['to_email'].widget.attrs['readonly'] = True
        self.fields['subject'].widget.attrs['readonly'] = True
        self.fields['message_format'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True

    class Meta:
        model = EmailTemplateModel
        fields = ("name", "key", "from_email", "to_email",
                  "subject", "message_format", 'status')
        readonly_fields = ["name"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'from_email': forms.TextInput(attrs={'class': 'form-control'}),
            'to_email': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message_format': Textarea(attrs={'cols': 3, 'rows': 3}),
        }
