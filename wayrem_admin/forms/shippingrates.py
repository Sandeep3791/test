from ckeditor.widgets import CKEditorWidget
from django.forms import Textarea, ModelChoiceField
from django import forms
from django.forms import widgets
from wayrem_admin.models import ShippingRates


class ShippingRatesForm(forms.ModelForm):

    class Meta:
        model = ShippingRates
        fields = ("from_dest", "to_dest", "price")
        widgets = {
            'from_dest': forms.TextInput(attrs={'class': 'form-control','type':'number'}),
            'to_dest': forms.TextInput(attrs={'class': 'form-control','type':'number'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ShippingRatesFilterForm(forms.ModelForm):
    search = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control p-2'}),required=False)
    class Meta:
        model = ShippingRates
        fields = ("search",)
        