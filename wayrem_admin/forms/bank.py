from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea, ModelChoiceField, CharField
from django import forms
from django.forms import widgets
from wayrem_admin.models import Orders, OrderTransactions, StatusMaster
from wayrem_admin.models.BankModels import Banks
from django.forms import ModelForm

from wayrem_admin.utils.constants import *
from wayrem_admin.models.BankModels import Banks


class BankUpdatedForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    bank_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    account_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    account_no = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=True)
    swift_code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=True)
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    branch = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)
    iban = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=False)

    choice_status = (("1", "Active"), ("0", "In Active"))
    status = forms.ChoiceField(choices=choice_status, widget=forms.Select(
        attrs={'class': 'form-control form-control-select', }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Banks
        fields = ['title', 'bank_name', 'account_name', 'account_no',
                  'swift_code', 'city', 'branch', 'iban', 'status']


class BankViewForm(forms.ModelForm):
    get_status_dict = {0: 'In Active', 1: 'Active'}
    status_choices = list(get_status_dict.items())
    #status_choices.insert(0,('','Select Status'))
    status = forms.ChoiceField(choices=status_choices, widget=forms.Select(
        attrs={'class': 'form-control form-control-select', 'disabled': 'disabled'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['readonly'] = True
        self.fields['bank_name'].widget.attrs['readonly'] = True
        self.fields['account_name'].widget.attrs['readonly'] = True
        self.fields['account_no'].widget.attrs['readonly'] = True
        self.fields['swift_code'].widget.attrs['readonly'] = True
        self.fields['city'].widget.attrs['readonly'] = True
        self.fields['branch'].widget.attrs['readonly'] = True
        self.fields['iban'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True

    class Meta:
        model = Banks
        fields = ['title', 'bank_name', 'account_name', 'account_no',
                  'swift_code', 'city', 'branch', 'iban', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'swift_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BankFilterForm(ModelForm):
    q = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control p-2'}), required=False)

    class Meta:
        model = Banks
        fields = ['q']
